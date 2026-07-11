from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Release(Base):
    __tablename__ = "releases"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    artist: Mapped[str]
    url: Mapped[str | None] = mapped_column(default=None)
    notified_at: Mapped[datetime] = mapped_column(server_default=func.now())
