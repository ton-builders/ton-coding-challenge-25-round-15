import os
import asyncio
import json
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","sticker_session")
OUT_DIR = os.environ.get("STICKER_DIR", "stickers")
META_FILE = os.path.join(OUT_DIR, "meta.json")

os.makedirs(OUT_DIR, exist_ok=True)

client = TelegramClient(SESSION, API_ID, API_HASH)

def load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_meta(data):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@client.on(events.NewMessage)
async def handler(event):
    if event.message.sticker:
        file_path = await client.download_media(event.message, file=OUT_DIR)
        meta = load_meta()
        meta.append({
            "id": event.message.id,
            "from": event.sender_id,
            "file": file_path,
            "date": str(event.date)
        })
        save_meta(meta)
        await event.reply(f"Sticker saved to {file_path}")

async def main():
    await client.start()
    print("Sticker saver running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
