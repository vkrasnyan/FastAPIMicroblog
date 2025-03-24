import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.models.like import Like


class TestLikeModel:
    @pytest.mark.asyncio
    async def test_fields(self, async_session: AsyncSession) -> None:
        current_fields_name = [i.name for i in Like.__table__.columns]
        related_fields = [
            i._dependency_processor.key for i in Like.__mapper__.relationships
        ]
        all_model_fields = current_fields_name + related_fields
        schema_fields_name = {
            "user_id",
            "tweet_id",
        }
        for field in schema_fields_name:
            assert field in all_model_fields, (
                "Нет необходимого поля %s" % field
            )
