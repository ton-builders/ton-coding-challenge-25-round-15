# summarizer_mock.py
import os, logging
from collections import deque
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "sum.session")
WINDOW = int(os.getenv("SUMMARY_WINDOW", "10"))

logging.basicConfig(level=logging.INFO)
client = TelegramClient(SESSION, API_ID, API_HASH)
buffers = {}  # chat_id -> deque

@client.on(events.NewMessage(incoming=True))
async def buffer_message(ev):
    cid = ev.chat_id
    buffers.setdefault(cid, deque(maxlen=WINDOW)).append((await ev.get_sender()).id if await ev.get_sender() else None, ev.raw_text or "")

@client.on(events.NewMessage(pattern=r"/summarize", incoming=True))
async def summarize(ev):
    cid = ev.chat_id
    buf = buffers.get(cid)
    if not buf:
        await ev.reply("No recent messages")
        return
    text = "\n".join(msg for _uid, msg in list(buf))
    # mock summarization: take first 500 chars
    summary = text[:500] + ("..." if len(text) > 500 else "")
    await ev.reply(f"Summary:\n{summary}")

if __name__ == "__main__":
    client.start(); client.run_until_disconnected()
