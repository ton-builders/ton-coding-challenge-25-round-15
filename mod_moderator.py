# mod_moderator.py
import os, asyncio, logging
from datetime import datetime, timedelta
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "mod.session")
THRESH = int(os.getenv("SPAM_LINK_THRESHOLD", "3"))
BANNED = {w.strip().lower() for w in os.getenv("BANNED_WORDS", "spam,scam").split(",") if w.strip()}

logging.basicConfig(level=logging.INFO)
bot = TelegramClient(SESSION, API_ID, API_HASH)
_rate = {}

def touch(uid):
    now = datetime.utcnow()
    _rate.setdefault(uid, []).append(now)
    cutoff = now - timedelta(seconds=60)
    _rate[uid] = [t for t in _rate[uid] if t >= cutoff]

@bot.on(events.NewMessage(incoming=True))
async def handle(ev):
    sender = await ev.get_sender(); uid = getattr(sender, "id", 0)
    text = (ev.raw_text or "")
    if any(s in text for s in ("http://", "https://", "t.me/")):
        touch(uid)
        if len(_rate.get(uid, [])) >= THRESH:
            try:
                await ev.delete()
                await bot.send_message(uid, "Message removed: spam links")
                logging.info("Deleted spam from %s", uid)
            except Exception as e:
                logging.warning("Moderation failed: %s", e)
            return
    low = text.lower()
    if any(b in low for b in BANNED):
        try:
            await ev.delete()
            await bot.send_message(uid, "Message removed: banned content")
        except Exception:
            pass

if __name__ == "__main__":
    bot.start(); bot.run_until_disconnected()
