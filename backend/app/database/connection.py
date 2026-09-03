from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Support both PostgreSQL (production) and SQLite (local dev fallback).
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Create all tables."""
    import app.models  # noqa: F401  ensure models are registered
    Base.metadata.create_all(bind=engine)
    # Keep local databases created before conversation threading compatible.
    columns = {column["name"] for column in inspect(engine).get_columns("ai_conversations")}
    if "conversation_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE ai_conversations ADD COLUMN conversation_id VARCHAR(36)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
