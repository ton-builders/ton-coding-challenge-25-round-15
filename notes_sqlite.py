
import os
import asyncio
import sqlite3
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID","0"))
API_HASH = os.environ.get("API_HASH","")
SESSION = os.environ.get("SESSION","notes_session")
DB_PATH = os.environ.get("NOTES_DB", "notes.db")

client = TelegramClient(SESSION, API_ID, API_HASH)

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def add_note(user_id, title, content):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                (user_id, title, content))
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    return nid

def list_notes(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM notes WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_note(user_id, nid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM notes WHERE user_id=? AND id=?", (user_id, nid))
    row = cur.fetchone()
    conn.close()
    return row

def delete_note(user_id, nid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE user_id=? AND id=?", (user_id, nid))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted

@client.on(events.NewMessage(pattern=r'^/note\s+(.+)', outgoing=False))
async def handler(event):
    cmd = event.pattern_match.group(1).strip()
    parts = cmd.split(maxsplit=1)
    sub = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    uid = event.sender_id

    if sub == "add":
        # format: add Title | Content
        if "|" not in arg:
            await event.reply("Usage: /note add Title | Content")
            return
        title, content = [p.strip() for p in arg.split("|", 1)]
        nid = add_note(uid, title, content)
        await event.reply(f"Saved note #{nid}")
    elif sub == "list":
        rows = list_notes(uid)
        if not rows:
            await event.reply("No notes yet.")
            return
        text = "\n".join([f"{r[0]}: {r[1]} ({r[2]})" for r in rows])
        await event.reply("Your notes:\n" + text)
    elif sub == "get":
        if not arg.isdigit():
            await event.reply("Usage: /note get ID")
            return
        row = get_note(uid, int(arg))
        if not row:
            await event.reply("Note not found.")
            return
        await event.reply(f"#{row[0]} {row[1]}\n\n{row[2]}\n\nCreated: {row[3]}")
    elif sub == "delete":
        if not arg.isdigit():
            await event.reply("Usage: /note delete ID")
            return
        deleted = delete_note(uid, int(arg))
        await event.reply("Deleted." if deleted else "Note not found.")
    else:
        await event.reply("Unknown subcommand. Use add, list, get, delete.")

async def main():
    init_db()
    await client.start()
    print("Notes bot running. Commands: /note add, list, get, delete")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
