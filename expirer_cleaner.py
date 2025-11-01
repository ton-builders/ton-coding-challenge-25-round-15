# expirer_cleaner.py
import os, logging
from datetime import datetime, timedelta
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "expire.session")
OWNER = int(os.getenv("OWNER_ID", "0"))

logging.basicConfig(level=logging.INFO)
client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r"/purge (\d+)", incoming=True))
async def purge(ev):
    user = await ev.get_sender()
    if getattr(user, "id", 0) != OWNER:
        await ev.reply("Access denied")
        return
    days = int(ev.pattern_match.group(1))
    cutoff = datetime.utcnow() - timedelta(days=days)
    chat = await ev.get_input_chat()
    count = 0
    async for msg in client.iter_messages(chat, limit=None):
        if msg.date.replace(tzinfo=None) < cutoff:
            try:
                await msg.delete()
                count += 1
            except Exception:
                pass
    await ev.reply(f"Removed {count} messages older than {days} days")

if __name__ == "__main__":
    client.start(); client.run_until_disconnected()
