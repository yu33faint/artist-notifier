import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_PATH = "notifier.db"
DATABASE_URL = "sqlite:///./notifier.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    conn = get_db_connection()
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