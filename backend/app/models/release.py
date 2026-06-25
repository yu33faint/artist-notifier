from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Release(Base):
    __tablename__ = "releases"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    artist: Mapped[str]