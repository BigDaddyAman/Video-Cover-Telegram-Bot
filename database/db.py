import aiosqlite

DB_FILE = "users.db"


async def get_db():
    db = await aiosqlite.connect(DB_FILE)

    await db.execute("PRAGMA journal_mode=WAL;")
    await db.execute("PRAGMA busy_timeout=5000;")

    return db


async def init_db():
    db = await get_db()

    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        """)
        await db.commit()
    finally:
        await db.close()


async def add_user(user_id: int):
    db = await get_db()

    try:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()
    finally:
        await db.close()