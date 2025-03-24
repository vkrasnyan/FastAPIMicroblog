import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import User, Follow


@pytest_asyncio.fixture
async def test_followers(async_session: AsyncSession, test_user: User):
    follower = User(name="Follower", api_key="follower_api_key")
    async_session.add(follower)
    await async_session.commit()
    await async_session.refresh(follower)

    follow = Follow(leader_id=test_user.id, followed_id=follower.id)
    async_session.add(follow)
    await async_session.commit()
    return follow
