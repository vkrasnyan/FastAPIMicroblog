import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.like import Like
from blogapp.models.user import User
from tests.fixtures.test_user import user_fixture
from tests.fixtures.test_tweet import test_tweets


@pytest_asyncio.fixture
async def test_likes(async_session: AsyncSession, user_fixture: User, test_tweets):
    likes = [Like(user_id=user_fixture.id, tweet_id=tweet.id) for tweet in test_tweets]
    async_session.add_all(likes)
    await async_session.commit()
    return likes
