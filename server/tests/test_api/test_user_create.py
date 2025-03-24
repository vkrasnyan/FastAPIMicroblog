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
        self,
        async_session: AsyncSession,
        user_fixture: User,
        async_client: AsyncClient,
    ) -> None:
        """Проверка создания пользователя"""
        data = UserCreate(
            name=user_fixture.name,
            api_key=user_fixture.api_key
        )
        response = await async_client.post(
            ROOT_ENDPOINT,
            json=data.model_dump(),
            follow_redirects=True
        )
        assert response.status_code == 200

        created_user = await get_current_user(
            api_key=user_fixture.api_key,
            session=async_session
        )
        assert created_user is not None

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

        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"

        query = await async_session.execute(
            select(User).where(User.api_key == user_fixture.api_key)
        )
        users = query.scalars().all()

        assert len(users) == 1
