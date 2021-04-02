from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from common import SETTINGS

engine = create_async_engine(SETTINGS.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
    future=True,
)


@asynccontextmanager
async def get_db() -> AsyncGenerator:
    """
    Open a new session to the database
    """
    try:
        async with SessionLocal() as session:
            yield session
    finally:
        await session.close()
