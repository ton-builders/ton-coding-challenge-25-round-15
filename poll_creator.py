import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Poll, PollAnswer

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","poll_session")

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'^/poll\s+(.+)'))
async def handler(event):
    """Create a native Telegram poll. Format: /poll Question | Option1 | Option2 | ..."""
    body = event.pattern_match.group(1)
    parts = [p.strip() for p in body.split("|") if p.strip()]
    if len(parts) < 3:
        await event.reply("Usage: /poll Question | Option1 | Option2 (min 2 options)")
        return
    question = parts[0]
    options = parts[1:]
    # Build poll answers
    answers = [PollAnswer(text=opt, option=b"%d" % i) for i, opt in enumerate(options)]
    # send poll (Quiz false)
    await client.send_message(event.chat_id, file=None, poll=Poll(
        id=0,  # server assigns id
        question=question,
        answers=answers,
        closed=False,
        public_voters=False,
        multiple_choice=False
    ))
    await event.reply("Poll created.")

async def main():
    await client.start()
    print("Poll creator ready.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
