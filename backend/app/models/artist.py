from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
