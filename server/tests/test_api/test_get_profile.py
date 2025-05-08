import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from blogapp.models import User
from tests.fixtures.test_user import user_fixture

ROOT_ENDPOINT = "/api/users/me"

@pytest.mark.asyncio
async def test_get_my_profile(
        async_session: AsyncSession,
        user_fixture: User,
        async_client: AsyncClient,
):
    headers = {
        "api-key": user_fixture.api_key
    }
    response = await async_client.get(ROOT_ENDPOINT, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["id"] == user_fixture.id
    assert data["user"]["name"] == user_fixture.name
    assert data["user"]["followers"] == []
    assert data["user"]["following"] == []
