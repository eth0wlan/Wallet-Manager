from pathlib import Path
import sqlite3

Path("data").mkdir(exist_ok=True)

database = sqlite3.connect("data/walletdb.db")
cursor = database.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    money INTEGER DEFAULT 0
)
""")

database.commit()


def get_wallet(user_id):
    cursor.execute(
        "SELECT money FROM wallets WHERE tg_id = ?",
        (user_id,)
    )

    return cursor.fetchone()


def add_wallet(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO wallets (tg_id, money) VALUES (?, ?)",
        (user_id, 0)
    )

    database.commit()

def add_money(user_id, amount):
    cursor.execute(
        """
        UPDATE wallets
        SET money = money + ?
        WHERE tg_id = ?
        """,
        (amount, user_id)
    )

    database.commit()


def remove_money(user_id, amount):
    cursor.execute(
        """
        UPDATE wallets
        SET money = money - ?
        WHERE tg_id = ?
        """,
        (amount, user_id)
    )

    database.commit()    