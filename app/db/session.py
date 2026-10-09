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
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all tables from the SQLAlchemy models and auto-migrate SQLite columns."""
    import app.models  # Ensure mappers are loaded
    Base.metadata.create_all(bind=engine)

    if "sqlite" in settings.database_url:
        with engine.connect() as conn:
            from sqlalchemy import inspect, text
            inspector = inspect(engine)
            if "products" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("products")]
                if "embedding_data" not in columns:
                    conn.execute(text("ALTER TABLE products ADD COLUMN embedding_data TEXT"))
                    conn.commit()



def get_db_session() -> Session:
    """Create a database session bound to the engine."""
    return SessionLocal()
