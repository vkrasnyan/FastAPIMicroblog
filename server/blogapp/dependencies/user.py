from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from server.blogapp.models import User
from .session import get_async_session


async def get_current_user(
        api_key: str = Header(...),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Зависимость для получения текущего пользователя по api_key.
    """
    query = await session.execute(select(User).where(User.api_key == api_key))
    user = query.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid API key")

    return user