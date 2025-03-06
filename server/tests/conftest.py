import pytest_asyncio

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from server.blogapp.database import Base, get_async_session
from server.blogapp.main import app


# Создаем тестовую базу данных (SQLite in-memory)
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Настройка SQLAlchemy для тестовой базы данных
engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


# Переопределяем зависимость get_session для использования тестовой базы данных
async def override_get_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

# Применяем переопределение зависимости
app.dependency_overrides[get_async_session] = override_get_session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Функция для создания базы данных перед каждым тестом"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def async_session() -> AsyncSession:
    """Фикстура для передачи сессии в тесты"""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db):
    """Функция для создания тестового клиента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
