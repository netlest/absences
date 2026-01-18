"""
Database connection and session management.
Best practice: Use SQLAlchemy 2.0 style with async support capability.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from ..core.config import settings

# Best practice: Create engine with proper connection pooling
# For production, consider using async engine with asyncpg
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,         # Connection pool size
    max_overflow=20,      # Max connections beyond pool_size
    echo=False,           # Set to True for SQL query logging in development
)

# Best practice: Use sessionmaker for session factory pattern
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Best practice: Use declarative_base for model definitions
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Best practice: Use dependency injection for database sessions.
    
    This ensures:
    1. Each request gets its own session
    2. Sessions are properly closed after use
    3. Exceptions are handled correctly
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
