import datetime
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.user import User


@pytest_asyncio.fixture
async def user_fixture(async_session: AsyncSession) -> User:
    user = User(
        name="Ivan Petrov",
        api_key="key123456",
        created_at=datetime.datetime.utcnow()
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user
