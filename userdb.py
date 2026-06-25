from pathlib import Path
import sqlite3

Path("data").mkdir(exist_ok=True)

database = sqlite3.connect("data/userdb.db")
cursor = database.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    tg_id INTEGER PRIMARY KEY,
    name TEXT
)
""")

database.commit()


def get_user(user_id):
    cursor.execute(
        "SELECT * FROM users WHERE tg_id = ?",
        (user_id,)
    )

    return cursor.fetchone()


def add_user(user_id, name):
    cursor.execute(
        "INSERT OR IGNORE INTO users (tg_id, name) VALUES (?, ?)",
        (user_id, name)
    )

    database.commit()