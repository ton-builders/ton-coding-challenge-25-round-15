# group_stats.py
import os, logging
from collections import defaultdict
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "stats.session")
OWNER = int(os.getenv("OWNER_ID", "0"))

logging.basicConfig(level=logging.INFO)
client = TelegramClient(SESSION, API_ID, API_HASH)
counts = defaultdict(int)

@client.on(events.NewMessage(incoming=True))
async def count_message(ev):
    chat_id = ev.chat_id or 0
    counts[chat_id] += 1

@client.on(events.NewMessage(pattern=r"/stats", incoming=True))
async def send_stats(ev):
    user = await ev.get_sender()
    if getattr(user, "id", 0) != OWNER:
        await ev.reply("Access denied")
        return
    lines = [f"chat {k}: {v} messages" for k, v in counts.items()]
    await ev.reply("\n".join(lines) if lines else "No data yet")

if __name__ == "__main__":
    client.start(); client.run_until_disconnected()
