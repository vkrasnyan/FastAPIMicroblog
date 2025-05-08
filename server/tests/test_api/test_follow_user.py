import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models import User
from blogapp.schemas import UserCreate
import uuid

ROOT_ENDPOINT = "/api/users"
class TestFollowUser:
    @pytest.mark.asyncio
    async def test_follow_and_unfollow(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
    ):
        user1 = User(name="Alice", api_key=str(uuid.uuid4()))
        user2 = User(name="Bob", api_key=str(uuid.uuid4()))
        async_session.add_all([user1, user2])
        await async_session.commit()
        await async_session.refresh(user1)
        await async_session.refresh(user2)

        # Подписка: user1 -> user2
        response = await async_client.post(
            f"ROOT_ENDPOINT/{user2.id}/follow",
            headers={"api-key": user1.api_key}
        )
        assert response.status_code == 200
        assert response.json()["result"] is True

        # Проверка, что user1 теперь подписан на user2
        me_response = await async_client.get("ROOT_ENDPOINT/me", headers={"api-key": user1.api_key})
        data = me_response.json()
        assert any(f["id"] == user2.id for f in data["user"]["following"])

        # Проверка, что user2 имеет подписчика user1
        me_response_2 = await async_client.get("ROOT_ENDPOINT/me", headers={"api-key": user2.api_key})
        data_2 = me_response_2.json()
        assert any(f["id"] == user1.id for f in data_2["user"]["followers"])

        # Повторная подписка должна завершиться ошибкой
        response = await async_client.post(
            f"ROOT_ENDPOINT/{user2.id}/follow",
            headers={"api-key": user1.api_key}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Already following this user"

        # Отписка
        response = await async_client.delete(
            f"ROOT_ENDPOINT/{user2.id}/follow",
            headers={"api-key": user1.api_key}
        )
        assert response.status_code == 200
        assert response.json()["result"] is True

        # Проверка, что отписка прошла — user2 больше не в подписках
        me_response = await async_client.get("ROOT_ENDPOINT/me", headers={"api-key": user1.api_key})
        data = me_response.json()
        assert all(f["id"] != user2.id for f in data["user"]["following"])
