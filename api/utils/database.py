from typing import AsyncGenerator

from common.database import SessionLocal


async def get_db() -> AsyncGenerator:
    try:
        async with SessionLocal() as session:
            yield session
    finally:
        await session.close()
