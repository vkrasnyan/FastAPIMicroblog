import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from blogapp.models import Media, User

MEDIA_ENDPOINT = "/media"


class TestMediaEndpoints:

    @pytest.mark.asyncio
    async def test_upload_media_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        user_fixture: User
    ):
        file_content = b"fake image data"
        file = BytesIO(file_content)
        file.name = "test_image.jpg"

        response = await async_client.post(
            MEDIA_ENDPOINT + "/",
            files={"file": ("test_image.jpg", file, "image/jpeg")},
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] is True
        assert "media_id" in data

    @pytest.mark.asyncio
    async def test_upload_media_too_large(
        self,
        async_client: AsyncClient,
        user_fixture
    ):
        # Создаем файл больше 5MB
        big_file = BytesIO(b"x" * (5 * 1024 * 1024 + 1))
        big_file.name = "big_image.jpg"

        response = await async_client.post(
            MEDIA_ENDPOINT + "/",
            files={"file": ("big_image.jpg", big_file, "image/jpeg")},
            headers={"api-key": user_fixture.api_key},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "File size exceeds the limit of 5MB"

    @pytest.mark.asyncio
    async def test_get_media_success(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        file_content = b"some image content"
        media = Media(file_body=file_content, file_name="image.png", tweet_id=None)
        async_session.add(media)
        await async_session.commit()
        await async_session.refresh(media)

        response = await async_client.get(f"{MEDIA_ENDPOINT}/{media.id}")

        assert response.status_code == 200
        assert response.content == file_content
        assert response.headers["content-type"] == "image/png"

    @pytest.mark.asyncio
    async def test_get_media_not_found(
        self,
        async_client: AsyncClient
    ):
        response = await async_client.get(f"{MEDIA_ENDPOINT}/999999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Media not found"
