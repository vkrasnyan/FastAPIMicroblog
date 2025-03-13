import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from server.blogapp.models.tweet import Tweet
from server.blogapp.models.user import User


@pytest_asyncio.fixture
async def test_tweets(async_session: AsyncSession, test_user: User):
    tweets = [
        Tweet(content="First tweet", author_id=test_user.id),
        Tweet(content="Second tweet", author_id=test_user.id),
    ]
    async_session.add_all(tweets)
    await async_session.commit()
    return tweets
