# keyword_responder.py
import os, logging, yaml
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "kw.session")
CONFIG_PATH = os.getenv("KW_CONFIG", "keywords.yml")

logging.basicConfig(level=logging.INFO)
client = TelegramClient(SESSION, API_ID, API_HASH)

try:
    with open(CONFIG_PATH, "r", encoding="utf8") as f:
        mapping = yaml.safe_load(f) or {}
except Exception:
    mapping = {"hello": "Hi there!", "help": "Contact admin."}

@client.on(events.NewMessage(incoming=True))
async def reply_kw(ev):
    txt = (ev.raw_text or "").lower()
    for k, resp in mapping.items():
        if k in txt:
            await ev.reply(resp)
            return

if __name__ == "__main__":
    client.start(); client.run_until_disconnected()
