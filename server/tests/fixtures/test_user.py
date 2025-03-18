import datetime
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from server.blogapp.models import User


@pytest_asyncio.fixture
async def user_fixture(async_session: AsyncSession) -> User:
    user = User(
        name="Ivan Petrov",
        api_key=str(uuid.uuid4()),
        created_at=datetime.datetime.utcnow()
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    print(f"✅ FIXTURE: Created user ID: {user.id}")
    return user
