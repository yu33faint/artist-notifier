import sqlite3

DATABASE_PATH = "notifier.db"

def get_db_connetion():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    conn = get_db_connetion()
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS artists "
        "(id TEXT PRIMARY KEY, name TEXT)"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS releases "
        "(id TEXT PRIMARY KEY, name TEXT, artist TEXT)"
    )

    conn.commit()
    conn.close()