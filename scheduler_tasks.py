# scheduler_tasks.py
import os, asyncio, logging
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "sched.session")
ANN = int(os.getenv("ANNOUNCE_CHAT_ID", "0"))
INTERVAL = int(os.getenv("ANN_INTERVAL_SEC", "86400"))

logging.basicConfig(level=logging.INFO)
client = TelegramClient(SESSION, API_ID, API_HASH)

async def announcer():
    while True:
        if ANN:
            try:
                await client.send_message(ANN, "Automated announcement")
            except Exception:
                pass
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    client.start()
    loop = asyncio.get_event_loop()
    loop.create_task(announcer())
    client.run_until_disconnected()
