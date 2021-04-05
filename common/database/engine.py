from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, AsyncContextManager, Callable

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


async def get_db() -> AsyncGenerator:
    """
    Open a new session to the database
    """
    try:
        async with SessionLocal() as session:
            yield session
    finally:
        await session.close()


# Required since FastAPI cannot use context managers as dependencies
# Relevant issue: https://github.com/tiangolo/fastapi/issues/2212
db_context: Callable[[], AsyncContextManager[AsyncSession]] = asynccontextmanager(
    get_db
)
