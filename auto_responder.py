 auto_responder.py

import os
import asyncio
from telethon import TelegramClient, events

# Configure via environment variables: API_ID, API_HASH
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION", "auto_responder_session")

# Keywords -> reply mapping
KEYWORD_MAP = {
    "hello": "Hi! How can I help you?",
    "price": "Please check our pricing page: https://example.com/pricing",
    "help": "Send /commands to see what I can do."
}

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Respond to messages that contain configured keywords (case-insensitive)."""
    text = (event.raw_text or "").lower()
    for k, reply in KEYWORD_MAP.items():
        if k in text:
            # avoid responding to ourselves
            if event.out:
                return
            await event.reply(reply)
            return

async def main():
    await client.start()
    print("Auto-responder started. Listening for keywords:", list(KEYWORD_MAP.keys()))
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
