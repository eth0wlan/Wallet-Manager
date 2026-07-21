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

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    amount INTEGER,
    type TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)
database.commit()


def get_wallet(user_id):
    cursor.execute(
        "SELECT money FROM wallets WHERE tg_id = ?",
        (user_id,)
    )

    wallet = cursor.fetchone()

    if wallet is None:
        add_wallet(user_id)

        cursor.execute(
            "SELECT money FROM wallets WHERE tg_id = ?",
            (user_id,)
        )

        wallet = cursor.fetchone()

    return wallet

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
    cursor.execute(
        """
        INSERT INTO history (tg_id, amount, type)
        VALUES (?, ?, ?)
        """,
        (user_id, amount, "Пополнение")
    )

    database.commit()

def get_trans(user_id):
    cursor.execute(
        "SELECT amount, type, date FROM history WHERE tg_id = ?",
        (user_id,)
    )
    trans = cursor.fetchall()
    
    return trans
    
def remove_money(user_id, amount):
    cursor.execute(
        """
        UPDATE wallets
        SET money = money - ?
        WHERE tg_id = ?
        """,
        (amount, user_id)
    )
    cursor.execute(
        """
        INSERT INTO history (tg_id, amount, type)
        VALUES (?, ?, ?)
        """,
        (user_id, amount, "Снятие")
    )

    database.commit()    