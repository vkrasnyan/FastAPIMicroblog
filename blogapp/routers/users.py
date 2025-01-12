from fastapi import APIRouter, HTTPException, Depends, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from blogapp.models.user import User
from blogapp.schemas import UserCreate, UserResponse, UserUpdate
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


@router.get("/users/<id>", response_model=UserResponse)
async def find_user(id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Роут для получения информации о пользователе по id
    """
    query = await session.execute(select(User).where(User.id == id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User with this ID does not exist.")
    return user


@router.get("/users/me", response_model=UserResponse)
async def get_my_profile(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Роут для получения информации о своем профиле
    """
    query = await session.execute(select(User).where(User.api_key == api_key))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User with this API key does not exist.")
    return user


@router.put("/users/me", response_model=UserResponse)
async def update_user(
        api_key: str = Header(...),
        user_update: UserUpdate = Body(...),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для редактирования своего профиля
    """
    query = await session.execute(select(User).where(User.api_key == api_key))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User with this API key does not exist.")
        # Обновляем данные пользователя
    if user_update.name:
        user.name = user_update.name
    # Других полей, которые можно отредактировать, у нас в БД нет, но при желании можно добавить.

    # Сохраняем изменения в базе данных
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user