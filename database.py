import sqlite3

DATABASE_PATH = "session.db"


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS credentials (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def set_credential(key: str, value: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO credentials (key, value)
        VALUES (?, ?)
    """,
        (key, value),
    )
    conn.commit()
    conn.close()


def get_credential(key: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM credentials WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def clear_credentials():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials")
    conn.commit()
    conn.close()


# Initialize the database when the module is loaded
init_db()
