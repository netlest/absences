"""
Database configuration and session management for FastAPI application.
Uses SQLAlchemy 2.0 with async session support.
"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

# Get database URL from environment
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')

# Use asyncpg driver for async PostgreSQL operations
# For development with SQLite, use: "sqlite+aiosqlite:///./app.db"
if os.getenv('FLASK_ENV') == 'development':
    DATABASE_URL = "sqlite+aiosqlite:///./app.db"
else:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create async engine with proper pool settings
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
    poolclass=NullPool if os.getenv('FLASK_ENV') == 'development' else None,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides a database session.
    
    This is used with FastAPI's dependency injection system:
    @app.get("/items")
    async def read_items(db: AsyncSession = Depends(get_db)):
        ...
    
    Yields:
        AsyncSession: Database session that will be automatically closed.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
