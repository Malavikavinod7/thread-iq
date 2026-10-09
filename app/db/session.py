from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all tables from the SQLAlchemy models."""
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)




def get_db_session() -> Session:
    """Create a database session bound to the engine."""
    return SessionLocal()
