"""Database engine & session management.
Default: SQLite (zero-config demo).
Production: set DATABASE_URL to PostgreSQL (+ pgvector).
"""
from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

# Prefer explicit DATABASE_URL_SYNC; fall back to sqlite for local demo
_db_url = settings.DATABASE_URL_SYNC
if not _db_url or "localhost" in _db_url:
    # SQLite for easy local/demo use — persists to file
    _db_url = "sqlite:///./disease_ai.db"

connect_args = {}
if _db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        _db_url,
        connect_args=connect_args,
        poolclass=StaticPool,
        echo=False,
    )
else:
    engine = create_engine(_db_url, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
