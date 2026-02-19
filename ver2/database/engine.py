"""Database engine and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from config import DATABASE_URL
from database.models import Base


# Async engine for application
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
