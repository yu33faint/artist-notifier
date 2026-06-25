from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models.release import Release


def get_all_release_ids() -> set[str]:
    session = SessionLocal()

    try:
        release_ids = session.scalars(select(Release.id)).all()

        return set(release_ids)
    finally:
        session.close()


def save_releases(releases: list[tuple[str, str, str]]) -> None:
    session = SessionLocal()

    try:
        release_records = [
            Release(
                id=release_id,
                name=release_name,
                artist=artist_name,
            )
            for release_id, release_name, artist_name in releases
        ]

        session.add_all(release_records)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
