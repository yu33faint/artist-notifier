from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from backend.app.database import get_session
from backend.app.models.artist import Artist


def get_all_artist_records() -> list[tuple[str, str]]:
    with get_session() as session:
        artists = session.scalars(select(Artist)).all()
        return [(artist.id, artist.name) for artist in artists]


def get_all_artists() -> list[dict[str, str]]:
    return [
        {"id": artist_id, "name": artist_name}
        for artist_id, artist_name in get_all_artist_records()
    ]


def create_artist(artist_id: str, artist_name: str) -> bool:
    with get_session() as session:
        artist = Artist(id=artist_id, name=artist_name)
        session.add(artist)
        try:
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False


def delete_artist_by_id(artist_id: str) -> bool:
    with get_session() as session:
        result = session.execute(
            delete(Artist).where(Artist.id == artist_id)
        )
        session.commit()
        return result.rowcount > 0
