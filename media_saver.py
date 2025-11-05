
import os
import asyncio
from telethon import TelegramClient, events
from datetime import datetime

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","media_saver_session")
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads_media")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
client = TelegramClient(SESSION, API_ID, API_HASH)

def log(s):
    print(f"[{datetime.now().isoformat()}] {s}")

@client.on(events.NewMessage(pattern=r'^/save\s*(\d+)?', outgoing=False))
async def save_handler(ev):
    amount = int(ev.pattern_match.group(1) or 10)
    log(f"Requested save {amount} items in chat {ev.chat_id}")
    msgs = await client.get_messages(ev.chat_id, limit=500)
    saved = 0
    for m in msgs:
        if saved >= amount:
            break
        if m.media:
            path = await client.download_media(m.media, file=DOWNLOAD_DIR)
            saved += 1
            await ev.reply(f"Saved: {os.path.basename(path)}")
    await ev.reply(f"Done. Saved {saved} media files to {DOWNLOAD_DIR}")
    log(f"Finished save: {saved}")

async def main():
    await client.start()
    log("Media saver running.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
