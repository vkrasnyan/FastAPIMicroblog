from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from blogapp.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
    )

Base = declarative_base()

# Зависимость для получения сессии
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session