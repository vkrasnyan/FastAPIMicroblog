import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import Tweet, Like, User
from tests.fixtures.test_user import user_fixture

TWEET_ENDPOINT = "/api/tweets"


class TestTweetLikes:

    @pytest.mark.asyncio
    async def test_like_tweet_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        tweet = Tweet(content="Like me!", author_id=user_fixture.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        response = await async_client.post(
            f"{TWEET_ENDPOINT}/{tweet.id}/likes",
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 200
        assert response.json() == {"result": True}

        like_exists = await async_session.execute(
            select(Like).where(Like.user_id == user_fixture.id, Like.tweet_id == tweet.id)
        )
        assert like_exists.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_like_nonexistent_tweet(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        response = await async_client.post(
            f"{TWEET_ENDPOINT}/999999/likes",
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "No such tweet"

    @pytest.mark.asyncio
    async def test_unlike_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        tweet = Tweet(content="Unlikable tweet", author_id=user_fixture.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        like = Like(user_id=user_fixture.id, tweet_id=tweet.id)
        async_session.add(like)
        await async_session.commit()

        response = await async_client.delete(
            f"{TWEET_ENDPOINT}/{tweet.id}/likes",
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 200
        assert response.json() == {"result": True}

        like_check = await async_session.execute(
            select(Like).where(Like.user_id == user_fixture.id, Like.tweet_id == tweet.id)
        )
        assert like_check.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unlike_nonexistent_like(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        tweet = Tweet(content="Never liked", author_id=user_fixture.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        response = await async_client.delete(
            f"{TWEET_ENDPOINT}/{tweet.id}/likes",
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "You haven't marked this like"
