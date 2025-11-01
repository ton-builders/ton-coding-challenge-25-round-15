# auto_forwarder.py
import os, logging
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "fwd.session")
CHAT_A = int(os.getenv("CHAT_A_ID", "0"))   # source
CHAT_B = int(os.getenv("CHAT_B_ID", "0"))   # destination

logging.basicConfig(level=logging.INFO)
app = TelegramClient(SESSION, API_ID, API_HASH)

@app.on(events.NewMessage(chats=CHAT_A))
async def forward_a(ev):
    await app.forward_messages(CHAT_B, ev.message)
    logging.info("Forwarded message %s -> %s", CHAT_A, CHAT_B)

@app.on(events.NewMessage(chats=CHAT_B))
async def forward_b(ev):
    await app.forward_messages(CHAT_A, ev.message)
    logging.info("Forwarded message %s -> %s", CHAT_B, CHAT_A)

if __name__ == "__main__":
    app.start(); app.run_until_disconnected()
