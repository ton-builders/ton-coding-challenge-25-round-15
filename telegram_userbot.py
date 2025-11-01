# telegram_userbot.py
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from telethon import TelegramClient, events
from telethon.errors import RPCError

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "userbot.session")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
ANNOUNCE_CHAT_ID = int(os.getenv("ANNOUNCE_CHAT_ID", "0"))
SPAM_LINK_THRESHOLD = int(os.getenv("SPAM_LINK_THRESHOLD", "3"))
BANNED_WORDS = set(
    w.strip().lower()
    for w in os.getenv("BANNED_WORDS", "spam,scam,phish").split(",")
    if w.strip()
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("userbot")


class RateTracker:
    def __init__(self):
        self._events: Dict[int, List[datetime]] = {}

    def add(self, user_id: int) -> None:
        self._events.setdefault(user_id, []).append(datetime.utcnow())
        self._cleanup(user_id)

    def count_recent(self, user_id: int, window_seconds: int = 60) -> int:
        self._cleanup(user_id, window_seconds)
        return len(self._events.get(user_id, []))

    def _cleanup(self, user_id: int, window_seconds: int = 60) -> None:
        now = datetime.utcnow()
        arr = self._events.get(user_id, [])
        self._events[user_id] = [t for t in arr if (now - t).total_seconds() <= window_seconds]
        if not self._events[user_id]:
            self._events.pop(user_id, None)


class Userbot:
    def __init__(self, api_id: int, api_hash: str, session: str):
        if not api_id or not api_hash:
            raise ValueError("API_ID and API_HASH must be set.")
        self.client = TelegramClient(session, api_id, api_hash)
        self.rate_tracker = RateTracker()
        self._announce_task: Optional[asyncio.Task] = None

    async def start(self):
        await self.client.start()
        me = await self.client.get_me()
        logger.info("Running as %s (id=%s)", me.username or me.first_name, me.id)
        self._register_handlers()
        if ANNOUNCE_CHAT_ID:
            self._announce_task = asyncio.create_task(self._announcement_worker())

    def _register_handlers(self):
        @self.client.on(events.NewMessage(incoming=True))
        async def on_message(event):
            await self._on_new_message(event)

        @self.client.on(events.NewMessage(pattern=r"/faq(?: |$)(.*)", incoming=True))
        async def on_faq(event):
            await self._handle_faq(event)

        @self.client.on(events.NewMessage(pattern=r"/owner (.+)", incoming=True))
        async def on_owner_command(event):
            await self._handle_owner_command(event)

    async def _on_new_message(self, event):
        sender = await event.get_sender()
        sender_id = sender.id if sender else 0
        text = (event.raw_text or "").strip()

        if any(link in text for link in ("http://", "https://", "t.me/")):
            self.rate_tracker.add(sender_id)
            link_count = self.rate_tracker.count_recent(sender_id)
            if link_count >= SPAM_LINK_THRESHOLD and not await self._is_admin(event, sender_id):
                await self._moderate_delete_and_warn(event, "excessive links")
                return

        lower = text.lower()
        if any(bw in lower for bw in BANNED_WORDS) and not await self._is_admin(event, sender_id):
            await self._moderate_delete_and_warn(event, "banned words")
            return

        if event.is_private and sender_id != (await self.client.get_me()).id:
            await asyncio.sleep(0.2)
            await self.client.send_message(sender_id, "Hello! Use /faq <topic> for quick info.")

    async def _is_admin(self, event, user_id: int) -> bool:
        try:
            chat = await event.get_chat()
            if not hasattr(chat, "participants_count"):
                return False
            admins = [a.user_id for a in await self.client.get_participants(chat, filter=None)]
            return user_id in admins
        except Exception:
            return False

    async def _moderate_delete_and_warn(self, event, reason: str):
        try:
            who = await event.get_sender()
            await event.delete()
            logger.info("Deleted message from %s (%s)", getattr(who, 'id', '?'), reason)
            await self.client.send_message(
                getattr(who, 'id', None) or event.chat_id,
                f"Your message was removed: {reason}.",
            )
        except RPCError as e:
            logger.warning("Moderation error: %s", e)

    async def _handle_faq(self, event):
        topic = (event.pattern_match.group(1) or "").strip().lower()
        if not topic:
            await event.reply("Usage: /faq <topic>")
            return
        faq_db = {
            "rules": "Be polite. Avoid spam links.",
            "rewards": "Rewards are distributed weekly.",
        }
        answer = faq_db.get(topic, "Unknown topic.")
        await event.reply(answer)

    async def _handle_owner_command(self, event):
        sender = await event.get_sender()
        if sender.id != OWNER_ID:
            await event.reply("Access denied.")
            return
        body = event.pattern_match.group(1).strip()
        if body == "status":
            await event.reply(f"Running. Tracked users: {len(self.rate_tracker._events)}")
        elif body.startswith("announce "):
            msg = body[len("announce "):]
            await self._post_announcement(msg)
            await event.reply("Announcement sent.")
        elif body == "stop_announce":
            if self._announce_task:
                self._announce_task.cancel()
                self._announce_task = None
                await event.reply("Announcements stopped.")
            else:
                await event.reply("No active announcement task.")
        else:
            await event.reply("Unknown command.")

    async def _post_announcement(self, text: str):
        if not ANNOUNCE_CHAT_ID:
            logger.warning("ANNOUNCE_CHAT_ID not configured.")
            return
        try:
            await self.client.send_message(ANNOUNCE_CHAT_ID, text)
            logger.info("Announcement posted to %s", ANNOUNCE_CHAT_ID)
        except Exception as e:
            logger.error("Announcement error: %s", e)

    async def _announcement_worker(self):
        logger.info("Announcement worker started for %s", ANNOUNCE_CHAT_ID)
        try:
            while True:
                await self._post_announcement("Daily reminder: check pinned messages.")
                await asyncio.sleep(24 * 3600)
        except asyncio.CancelledError:
            logger.info("Announcement worker stopped.")
        except Exception as e:
            logger.error("Announcement worker exception: %s", e)

    async def stop(self):
        if self._announce_task:
            self._announce_task.cancel()
        await self.client.disconnect()
        logger.info("Userbot stopped.")


if __name__ == "__main__":
    import signal

    bot = Userbot(API_ID, API_HASH, SESSION)
    loop = asyncio.get_event_loop()

    async def main():
        await bot.start()
        while True:
            await asyncio.sleep(3600)

    def handle_signal(sig, frame):
        logger.info("Signal received, shutting down.")
        loop.create_task(bot.stop())

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(bot.stop())
