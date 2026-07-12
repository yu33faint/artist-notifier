from datetime import timezone

from sqlalchemy import select

from backend.app.database import get_session
from backend.app.models.release import Release


def get_all_release_ids() -> set[str]:
    with get_session() as session:
        release_ids = session.scalars(select(Release.id)).all()
        return set(release_ids)


def get_all_releases() -> list[dict]:
    with get_session() as session:
        releases = session.scalars(
            select(Release).order_by(Release.notified_at.desc())
        ).all()
        return [
            {
                "id": release.id,
                "name": release.name,
                "artist": release.artist,
                "url": release.url,
                "notified_at": release.notified_at.replace(tzinfo=timezone.utc).isoformat(),
            }
            for release in releases
        ]


def save_releases(releases: list[tuple[str, str, str, str]]) -> None:
    with get_session() as session:
        release_records = [
            Release(
                id=release_id,
                name=release_name,
                artist=artist_name,
                url=release_url,
            )
            for release_id, release_name, artist_name, release_url in releases
        ]

        session.add_all(release_records)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
