from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
_engine = None


class InMemorySession:
    """Fallback session object used when the database driver is unavailable."""

    def close(self) -> None:
        """Provide a no-op close method for compatibility with the session lifecycle."""
        return None


def get_engine():
    """Create the SQLAlchemy engine lazily and reuse it for the session factory."""
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(settings.database_url, pool_pre_ping=True)
        except ImportError:
            _engine = None
        if _engine is not None:
            SessionLocal.configure(bind=_engine)
    return _engine


def get_db_session() -> Session | InMemorySession:
    """Create a database session bound to the lazily initialized engine."""
    engine = get_engine()
    if engine is None:
        return InMemorySession()
    return SessionLocal()
