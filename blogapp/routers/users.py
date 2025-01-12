from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from blogapp.models.user import User
from blogapp.schemas import UserCreate, UserResponse
from ..database import get_async_session

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """
    Роут для создания пользователя.
    """
    # Проверяем, существует ли пользователь с таким api_key
    query = await session.execute(select(User).where(User.api_key == user.api_key))
    existing_user = query.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this API key already exists.")

    # Создаем нового пользователя
    new_user = User(name=user.name, api_key=user.api_key)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
