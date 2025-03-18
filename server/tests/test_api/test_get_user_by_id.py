import datetime
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from server.blogapp.models import User
from server.tests.fixtures.test_user import user_fixture

ROOT_ENDPOINT = "/api/users"


class TestGetUserbyID:
    @pytest.mark.asyncio
    async def test_get_user_by_id(
            self,
            async_session: AsyncSession,
            user_fixture: User,
            async_client: AsyncClient,
    ) -> None:

        response = await async_client.get(f"{ROOT_ENDPOINT}/{user_fixture.id}")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == user_fixture.id
        assert user_data["name"] == user_fixture.name
        assert user_data["api_key"] == user_fixture.api_key
