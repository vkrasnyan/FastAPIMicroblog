from fastapi import APIRouter, HTTPException, Depends, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from blogapp.models.tweet import Tweet
from blogapp.models.user import User
from blogapp.models.media import Media
from blogapp.dependencies.session import get_async_session
from blogapp.dependencies.user import get_current_user
from blogapp.schemas import TweetResponse, TweetCreate


router = APIRouter()


@router.post("/tweets", response_model=TweetResponse)
async def create_tweet(
    tweet_data: TweetCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для создания твита.
    """
    user = current_user
    new_tweet = Tweet(content=tweet_data.content, author_id=user.id)
    session.add(new_tweet)
    await session.commit()
    await session.refresh(new_tweet)

    if tweet_data.tweet_media_ids:
        media_objects = await session.execute(
            select(Media).filter(Media.id.in_(tweet_data.tweet_media_ids))
        )
        media_files = media_objects.scalars().all()
        for media in media_files:
            media.tweet_id = new_tweet.id  # Устанавливаем связь с твитом
        await session.commit()

        # Загружаем связанные медиафайлы
    media_query = await session.execute(
        select(Media).where(Media.tweet_id == new_tweet.id)
    )
    media_files = media_query.scalars().all()

    return new_tweet


@router.get("/tweets", response_model=TweetResponse)
async def get_tweets(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """Роут, возвращающий ленту пользователя"""
