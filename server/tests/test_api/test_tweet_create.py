import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import Tweet, User
from tests.fixtures.test_user import user_fixture

TWEET_ENDPOINT = "/api/tweets"


class TestCreateTweet:
    @pytest.mark.asyncio
    async def test_create_tweet_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        payload = {
            "tweet_data": "Hello, this is a test tweet!",
            "tweet_media_ids": []
        }

        response = await async_client.post(
            TWEET_ENDPOINT + "/",
            json=payload,
            headers={"api-key": user_fixture.api_key}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert "tweet_id" in data

        tweet = await async_session.get(Tweet, data["tweet_id"])
        assert tweet is not None
        assert tweet.content == payload["tweet_data"]
        assert tweet.author_id == user_fixture.id

    @pytest.mark.asyncio
    async def test_create_tweet_invalid_api_key(self, async_client: AsyncClient):
        payload = {
            "tweet_data": "This should fail",
            "tweet_media_ids": []
        }

        response = await async_client.post(
            TWEET_ENDPOINT + "/",
            json=payload,
            headers={"api-key": "invalid-api-key"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid API key"
