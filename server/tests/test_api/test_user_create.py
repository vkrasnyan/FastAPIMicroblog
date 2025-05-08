import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from blogapp.dependencies.user import get_current_user
from blogapp.models import User
from blogapp.schemas import UserCreate
from tests.fixtures.test_user import user_fixture

ROOT_ENDPOINT = "/api/users"


class TestUserCreate:
    @pytest.mark.asyncio
    async def test_create_success(
            async_client: AsyncClient,
            async_session: AsyncSession,
    ) -> None:
        """Проверка успешного создания пользователя"""
        user_data = UserCreate(
            name="Test User",
            api_key=str(uuid.uuid4())
        )

        response = await async_client.post(
            ROOT_ENDPOINT,
            json=user_data.model_dump(),
        )

        assert response.status_code == 200
        result = response.json()
        assert result["name"] == user_data.name
        assert result["api_key"] == user_data.api_key

    @pytest.mark.asyncio
    async def test_create_existing_user(
            self,
            async_client: AsyncClient,
            async_session: AsyncSession,
            user_fixture: User
    ) -> None:
        """
        Проверяем, что нельзя создать пользователя с уже существующим API-ключом.
        """
        payload = {
            "name": user_fixture.name,
            "api_key": user_fixture.api_key
        }

        response = await async_client.post("/users/", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "User with this API key already exists"

        query = await async_session.execute(
            select(User).where(User.api_key == user_fixture.api_key)
        )
        users = query.scalars().all()

        assert len(users) == 1
