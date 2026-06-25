from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from backend.app.database import SessionLocal
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
    session = SessionLocal()

    try:
        result = session.execute(
            delete(Artist).where(Artist.id == artist_id)
        )
        session.commit()
        return result.rowcount > 0
    finally:
        session.close()


def get_all_artist_records():
    session = SessionLocal()

    try:
        artists = session.scalars(select(Artist)).all()

        return [
            (
                artist.id,
                artist.name,
            )
            for artist in artists
        ]
    finally:
        session.close()
