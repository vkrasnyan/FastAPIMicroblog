import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import User, Tweet
from tests.fixtures.test_user import user_fixture

TWEET_ENDPOINT = "/api/tweets"


class TestDeleteTweet:
    @pytest.mark.asyncio
    async def test_delete_own_tweet_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        tweet = Tweet(content="To be deleted", author_id=user_fixture.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        response = await async_client.delete(
            f"{TWEET_ENDPOINT}/{tweet.id}/delete",
            headers={"api-key": user_fixture.api_key}
        )
        assert response.status_code == 200
        assert response.json()["result"] is True

        response_check = await async_client.get(f"{TWEET_ENDPOINT}/{tweet.id}")
        assert response_check.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tweet(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        response = await async_client.delete(
            f"{TWEET_ENDPOINT}/999999/delete",
            headers={"api-key": user_fixture.api_key}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "No such tweet"

    @pytest.mark.asyncio
    async def test_delete_tweet_not_author(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User,
    ):
        # Создаем чужого пользователя и твит
        other_user = User(name="Stranger", api_key=str(uuid.uuid4()))
        async_session.add(other_user)
        await async_session.commit()
        await async_session.refresh(other_user)
        tweet = Tweet(content="Not yours", author_id=other_user.id)
        async_session.add(tweet)
        await async_session.commit()
        await async_session.refresh(tweet)

        response = await async_client.delete(
            f"{TWEET_ENDPOINT}/{tweet.id}/delete",
            headers={"api-key": user_fixture.api_key}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "You are not authorized to delete this tweet"
