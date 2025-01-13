from fastapi import APIRouter, HTTPException, Depends, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import func

from blogapp.models.user import User
from blogapp.models.follow import Follow
from blogapp.schemas import UserCreate, UserResponse, UserUpdate
from ..database import get_async_session

router = APIRouter()

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

async def find_user_by_id(id: int, session: AsyncSession = Depends(get_async_session)) -> User:
    """
    Зависимость для получения пользователя по id.
    """
    query = await session.execute(select(User).where(User.id == id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid user id")
    return user

async def get_followers_and_following(user_id: int, session: AsyncSession):
    """
    Получает подписчиков и подписки для заданного пользователя.
    """
    # Получаем подписчиков
    followers_query = await session.execute(
        select(User.id, User.name)
        .join(Follow, Follow.leader_id == User.id)
        .where(Follow.followed_id == user_id)
    )
    followers = [{"id": row[0], "name": row[1]} for row in followers_query.fetchall()]

    # Получаем пользователей, на которых подписан пользователь
    following_query = await session.execute(
        select(User.id, User.name)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.leader_id == user_id)
    )
    following = [{"id": row[0], "name": row[1]} for row in following_query.fetchall()]

    return followers, following


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
async def find_user(
        existing_user: User = Depends(find_user_by_id),
        session: AsyncSession = Depends(get_async_session)
):
    user = existing_user
    followers, following = await get_followers_and_following(user.id, session)
    return {
        "id": user.id,
        "name": user.name,
        "api_key": user.api_key,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "followers": followers,
        "following": following,
    }


@router.get("/users/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для получения информации о своем профиле
    """
    user = current_user
    followers, following = await get_followers_and_following(user.id, session)

    return {
        "id": user.id,
        "name": user.name,
        "api_key": user.api_key,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "followers": followers,
        "following": following,
    }


@router.put("/users/me", response_model=UserResponse)
async def update_user(
        current_user: User = Depends(get_current_user),
        user_update: UserUpdate = Body(...),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для редактирования своего профиля
    """
    user = current_user
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
    current_user: User = Depends(get_current_user),
    existing_user: User = Depends(find_user_by_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для подписки на пользователя.
    """
    follower = current_user

    # Ищем пользователя, на которого подписываются
    followed = existing_user

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
    current_user: User = Depends(get_current_user),
    existing_user: User = Depends(find_user_by_id),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для отписки от пользователя.
    """

    follower = current_user

    # Ищем пользователя, от которого отписываются
    followed = existing_user

    query = await session.execute(
        select(Follow).where(Follow.leader_id == follower.id, Follow.followed_id == followed.id)
    )
    follow = query.scalar_one_or_none()

    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")

    await session.delete(follow)
    await session.commit()

    return {"result": True}

