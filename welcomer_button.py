# welcomer_button.py
import os, logging
from telethon import TelegramClient, events, Button

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "welcome.session")
WELCOME_CHAT = int(os.getenv("WELCOME_CHAT_ID", "0"))

logging.basicConfig(level=logging.INFO)
cl = TelegramClient(SESSION, API_ID, API_HASH)
pending = {}

@cl.on(events.ChatAction)
async def welcome(ev):
    if ev.user_joined or ev.user_added:
        user = await ev.get_user()
        uid = user.id
        pending[uid] = True
        await cl.send_message(uid, "Please accept the rules to participate.", buttons=Button.inline("Accept", data=b"accept"))

@cl.on(events.CallbackQuery)
async def on_cb(ev):
    uid = ev.sender_id
    if ev.data == b"accept" and pending.pop(uid, None):
        await ev.answer("Accepted")
        await cl.send_message(uid, "Welcome! You may now send messages.")

if __name__ == "__main__":
    cl.start(); cl.run_until_disconnected()
