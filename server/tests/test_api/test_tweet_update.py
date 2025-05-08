import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import Tweet, User
from tests.fixtures.test_user import user_fixture

TWEET_ENDPOINT = "/api/tweets"


class TestUpdateTweet:
    @pytest.mark.asyncio
    async def test_update_own_tweet_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        tweet = Tweet(content="Original content", author_id=user_fixture.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        updated_content = {"tweet_data": "Updated content"}

        response = await async_client.put(
            f"{TWEET_ENDPOINT}/{tweet.id}",
            json=updated_content,
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 200
        assert response.json()["tweet_data"] == updated_content["tweet_data"]

    @pytest.mark.asyncio
    async def test_update_tweet_not_author(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        # Создаем другого пользователя и его твит
        stranger = User(name="OtherUser", api_key=str(uuid.uuid4()))
        async_session.add(stranger)
        await async_session.commit()
        await async_session.refresh(stranger)

        tweet = Tweet(content="Someone else's tweet", author_id=stranger.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        updated_content = {"content": "Attempted unauthorized update"}

        response = await async_client.put(
            f"{TWEET_ENDPOINT}/{tweet.id}",
            json=updated_content,
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "You are not authorized to update this tweet"

    @pytest.mark.asyncio
    async def test_update_nonexistent_tweet(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        updated_content = {"content": "This won't work"}

        response = await async_client.put(
            f"{TWEET_ENDPOINT}/999999",
            json=updated_content,
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "No such tweet"
