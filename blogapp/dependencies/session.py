from sqlalchemy.ext.asyncio import AsyncSession
from ..database import async_session


async def get_async_session() -> AsyncSession:
    """Зависимость для получения сессии"""
    async with async_session() as session:
        yield session
