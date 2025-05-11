import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import User, Tweet
from tests.fixtures.test_user import user_fixture
from tests.fixtures.test_tweet import test_tweets

TWEET_ENDPOINT = "/api/tweets"


class TestGetTweets:
    @pytest.mark.asyncio
    async def test_get_all_tweets(
        self,
        async_session: AsyncSession,
        async_client: AsyncClient,
        user_fixture: User,
        test_tweets
    ):
        response = await async_client.get(
            TWEET_ENDPOINT + "/",
            headers={"api-key": user_fixture.api_key}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["result"] is True
        assert "tweets" in data
        assert len(data["tweets"]) == len(test_tweets)

        # Проверим, что контенты твитов совпадают
        returned_contents = [tweet["content"] for tweet in data["tweets"]]
        expected_contents = [tweet.content for tweet in test_tweets]
        assert returned_contents == expected_contents

    @pytest.mark.asyncio
    async def test_get_tweet_by_id_success(
            self,
            async_client: AsyncClient,
            test_tweets,
    ):
        tweet = test_tweets[0]
        response = await async_client.get(f"{TWEET_ENDPOINT}/{tweet.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tweet.id
        assert data["content"] == tweet.content
        assert isinstance(data["attachments"], list)

    @pytest.mark.asyncio
    async def test_get_tweet_by_id_not_found(self, async_client: AsyncClient):
        response = await async_client.get(f"{TWEET_ENDPOINT}/999999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Tweet not found"
