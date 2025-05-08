import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.tweet import Tweet
from blogapp.models.user import User
from tests.fixtures.test_user import user_fixture


@pytest_asyncio.fixture
async def test_tweets(async_session: AsyncSession, user_fixture: User):
    tweets = [
        Tweet(content="First tweet", author_id=user_fixture.id),
        Tweet(content="Second tweet", author_id=user_fixture.id),
    ]
    async_session.add_all(tweets)
    await async_session.commit()
    return tweets
