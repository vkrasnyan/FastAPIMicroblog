import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.like import Like
from blogapp.models.user import User


@pytest_asyncio.fixture
async def test_likes(async_session: AsyncSession, test_user: User, test_tweets):
    likes = [Like(user_id=test_user.id, tweet_id=tweet.id) for tweet in test_tweets]
    async_session.add_all(likes)
    await async_session.commit()
    return likes
