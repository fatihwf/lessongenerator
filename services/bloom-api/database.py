"""Database setup and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings
from logger import logger


def _make_engine():
    """Create engine with settings appropriate for the database type."""
    url = settings.database_url
    if url.startswith("sqlite"):
        # SQLite does not support connection pooling parameters
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
        )
    # PostgreSQL / other
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


engine = _make_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from models import (  # noqa: F401 - import to register with Base
        CurriculumItem,
        LearnerProfile,
        KnowledgeChunk,
        GeneratedLesson,
        FeedbackRecord,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
