from fastapi import APIRouter, HTTPException, Depends, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from blogapp.models.user import User
from blogapp.models.follow import Follow
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

@router.post("/users/{id}/follow")
async def follow_user(
    id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для подписки на пользователя.
    """
    # Ищем пользователя с указанным api_key
    query = await session.execute(select(User).where(User.api_key == api_key))
    follower = query.scalar_one_or_none()

    if not follower:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Ищем пользователя, на которого подписываются
    query = await session.execute(select(User).where(User.id == id))
    followed = query.scalar_one_or_none()

    if not followed:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, не подписан ли уже пользователь
    query = await session.execute(
        select(Follow).where(Follow.leader_id == follower.id, Follow.followed_id == followed.id)
    )
    existing_follow = query.scalar_one_or_none()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    # Создаем запись о подписке
    follow = Follow(leader_id=follower.id, followed_id=followed.id)
    session.add(follow)
    await session.commit()

    return {"result": True}


@router.delete("/users/{id}/follow")
async def unfollow_user(
    id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для отписки от пользователя.
    """

    query = await session.execute(select(User).where(User.api_key == api_key))
    follower = query.scalar_one_or_none()

    if not follower:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Ищем пользователя, от которого отписываются
    query = await session.execute(select(User).where(User.id == id))
    followed = query.scalar_one_or_none()

    if not followed:
        raise HTTPException(status_code=404, detail="User not found")

    query = await session.execute(
        select(Follow).where(Follow.leader_id == follower.id, Follow.followed_id == followed.id)
    )
    follow = query.scalar_one_or_none()

    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")

    await session.delete(follow)
    await session.commit()

    return {"result": True}

