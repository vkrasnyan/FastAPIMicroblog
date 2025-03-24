import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from blogapp.database import Base
from blogapp.dependencies.session import get_async_session
from blogapp.main import app

TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def override_get_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        print(f"⚠️ TEST DB USED: {session.bind.url}")
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Создаёт тестовую БД перед каждым тестом и переопределяет зависимости"""
    print("⚠️ Setting up TEST database...")

    app.dependency_overrides[get_async_session] = override_get_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очистка
        await conn.run_sync(Base.metadata.create_all)  # Создание заново

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очистка после тестов


@pytest_asyncio.fixture()
async def async_session() -> AsyncSession:
    """Фикстура для передачи сессии в тесты"""
    async with TestingSessionLocal() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture()
async def async_client():
    """Фикстура для тестового клиента"""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Использует единый event loop для всех тестов"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
