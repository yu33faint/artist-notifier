import sqlite3
from backend.app.database import get_db_connection

def get_all_artists():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name FROM artists")
        return [
            {
                "id": row[0],
                "name": row[1]
            }
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()

def create_artist(artist_id: str, artist_name: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO artists (id, name) VALUES (?, ?)",
            (artist_id, artist_name)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
