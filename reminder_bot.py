# reminder_bot.py
import os, asyncio, logging
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "reminder.session")

logging.basicConfig(level=logging.INFO)
svc = TelegramClient(SESSION, API_ID, API_HASH)

@svc.on(events.NewMessage(pattern=r"/remind (\d+)\s+(.+)", incoming=True))
async def schedule(ev):
    sender = await ev.get_sender(); uid = sender.id
    seconds = int(ev.pattern_match.group(1))
    text = ev.pattern_match.group(2).strip()
    await ev.reply(f"Reminder set in {seconds} seconds")
    async def job():
        await asyncio.sleep(seconds)
        try:
            await svc.send_message(uid, f"Reminder: {text}")
        except Exception:
            pass
    asyncio.create_task(job())

if __name__ == "__main__":
    svc.start(); svc.run_until_disconnected()
