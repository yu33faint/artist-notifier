import sqlite3

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.app.database import SessionLocal, get_db_connection
from backend.app.models.artist import Artist


def get_all_artists():
    session = SessionLocal()

    try:
        artists = session.scalars(select(Artist)).all()
        return [
            {
                "id": artist.id,
                "name": artist.name,
            }
            for artist in artists
        ]
    finally:
        session.close()


def create_artist(artist_id: str, artist_name: str) -> bool:
    session = SessionLocal()

    try:
        artist = Artist(
            id=artist_id,
            name=artist_name,
        )

        session.add(artist)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()


def delete_artist_by_id(artist_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM artists WHERE id = ?",
            (artist_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_artist_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name FROM artists")
        return cursor.fetchall()
    finally:
        conn.close()
