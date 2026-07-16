import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.database as database_module
from backend.app.database import Base
from backend.app.models.artist import Artist # noqa: F401 Base.metadataに登録するために必要
from backend.app.models.release import Release # noqa: F401


@pytest.fixture
def use_test_database(monkeypatch):
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(database_module, "SessionLocal", TestSessionLocal)

    yield

    test_engine.dispose()
