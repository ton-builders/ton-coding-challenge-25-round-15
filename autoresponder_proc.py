import os
import asyncio
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION", "sess_autoresp_v1")

KEYWORDS = {
    "hello": "Hello! How can I help?",
    "pricing": "Our pricing page: https://example.com/pricing",
    "help": "Type /commands to see available actions."
}

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def on_new_message(ev):
    text = (ev.raw_text or "").lower()
    if ev.out:  # ignore own outgoing messages
        return
    for k, resp in KEYWORDS.items():
        if k in text:
            await ev.reply(resp)
            return  # reply only once per message

async def main():
    await client.start()
    print("Auto-responder (procedural) started. Listening...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
