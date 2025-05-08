import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from blogapp.models import User, Follow
from blogapp.routers.users import get_followers_and_following
import uuid

@pytest.mark.asyncio
async def test_get_followers_and_following(async_session: AsyncSession):
    user_a = User(name="User A", api_key=str(uuid.uuid4()))
    user_b = User(name="User B", api_key=str(uuid.uuid4()))

    async_session.add_all([user_a, user_b])
    await async_session.flush()

    follow = Follow(leader_id=user_a.id, followed_id=user_b.id)
    async_session.add(follow)
    await async_session.commit()

    followers_b, following_b = await get_followers_and_following(user_b.id, async_session)
    assert {"id": user_a.id, "name": user_a.name} in followers_b
    assert following_b == []

    followers_a, following_a = await get_followers_and_following(user_a.id, async_session)
    assert {"id": user_b.id, "name": user_b.name} in following_a
    assert followers_a == []
