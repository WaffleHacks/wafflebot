from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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
