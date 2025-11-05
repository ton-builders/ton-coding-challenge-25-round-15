import os
import asyncio
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","text_transform_session")

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'^/upper\s+(.+)', outgoing=False))
async def upper_handler(event):
    text = event.pattern_match.group(1)
    await event.reply(text.upper())

@client.on(events.NewMessage(pattern=r'^/reverse\s+(.+)', outgoing=False))
async def reverse_handler(event):
    text = event.pattern_match.group(1)
    await event.reply(text[::-1])

async def main():
    await client.start()
    print("Text transform bot active. Commands: /upper, /reverse")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
