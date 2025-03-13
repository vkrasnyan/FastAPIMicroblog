from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from server.blogapp.dependencies.user import get_current_user
from server.blogapp.models import User
from server.blogapp.schemas import UserCreate


ROOT_ENDPOINT = "/api/users"


class TestUserCreate:
    async def test_create_succsess(
        self,
        async_session: AsyncSession,
        user_fixture: User,
        http_client: AsyncClient,
    ) -> None:
        data = UserCreate(api_key=user_fixture.api_key)
        response = await http_client.post(
            ROOT_ENDPOINT, json=data.model_dump()
        )
        assert response.status_code == 201
        await async_session.close()
        created_user = await get_current_user(
            api_key=user_fixture.api_key,
        )
        assert created_user is not None
