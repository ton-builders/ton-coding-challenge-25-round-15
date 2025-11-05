
import os
import asyncio
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","welcome_session")

WELCOME_TEXT = (
    "Welcome {name}!\n\n"
    "Please read the group rules:\n"
    "1) Be respectful.\n"
    "2) No spam.\n"
    "3) Use search before asking.\n\n"
    "If you need help, mention @admin."
)

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.ChatAction)
async def handler(event):
    """React to users joining the chat and send a welcome message in the same chat."""
    if event.user_joined or event.user_added:
        for user in (await event.get_users()):
            # Format the name and send welcome to the chat
            name = user.first_name or "there"
            await event.reply(WELCOME_TEXT.format(name=name))
            # optionally: send a private message (careful with privacy)
            # try:
            #     await client.send_message(user.id, "Welcome DM: ...")
            # except Exception:
            #     pass

async def main():
    await client.start()
    print("Welcome bot running.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
