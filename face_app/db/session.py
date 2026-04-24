"""Database engine and session management."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from face_app.db.models import Base

# Store the database in the user's home directory so it persists across runs.
_DB_DIR = Path.home() / ".face_app"
_DB_PATH = _DB_DIR / "face_app.db"


def _get_db_url() -> str:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{_DB_PATH}"


# Enable WAL mode and foreign-key enforcement for every SQLite connection.
@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _connection_record) -> None:
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Module-level singletons — created lazily on first call.
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            _get_db_url(),
            connect_args={"check_same_thread": False},  # safe for Qt background threads
            echo=False,
        )
    return _engine


def init_db() -> None:
    """Create all tables if they do not exist. Call once at application startup."""
    Base.metadata.create_all(bind=get_engine())


def _get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional database session.

    Usage::

        with get_session() as session:
            session.add(some_object)
    """
    factory = _get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
