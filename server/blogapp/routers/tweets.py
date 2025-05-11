import logging
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from blogapp.models.like import Like
from blogapp.models.tweet import Tweet
from blogapp.models.user import User
from blogapp.models.media import Media
from blogapp.models.follow import Follow
from blogapp.dependencies.session import get_async_session
from blogapp.dependencies.user import get_current_user
from blogapp.schemas import TweetCreate, TweetUpdate, TweetCreateResponse, TweetUpdateResponse

router = APIRouter()


@router.post("/", response_model=TweetCreateResponse)
async def create_tweet(
    tweet_data: TweetCreate,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session)
):
    # Логируем входящие данные
    logging.info(f"Received tweet data: {tweet_data}")
    logging.info(f"Received api_key: {api_key}")
    """
    Роут для создания твита.
    """
    # Получаем пользователя по api_key
    user_query = await session.execute(select(User).filter(User.api_key == api_key))
    user = user_query.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid API key")

    # Создаем твит
    new_tweet = Tweet(content=tweet_data.tweet_data, author_id=user.id)
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

    media_query = await session.execute(
        select(Media).where(Media.tweet_id == new_tweet.id)
    )
    media_files = media_query.scalars().all()

    return TweetCreateResponse(result=True, tweet_id=new_tweet.id)


@router.get("/", response_model=dict)
async def get_tweets(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Роут, возвращающий все записи пользователей. Сделан из-за несовершенства фронта, ибо иначе их не видно
    """
    user = current_user
    result = await session.execute(
        select(Tweet)
        .options(selectinload(Tweet.media))
        .order_by(Tweet.created_at.desc())
    )

    tweets = result.scalars().all()

    if tweets:
        return {
            "result": True,
            "tweets": [
                          {
                              "id": tweet.id,
                              "content": tweet.content,
                              "attachments": [
                                  f"/api/medias/{media.id}" for media in tweet.media
                              ],
                          }
                          for tweet in tweets
                      ]
        }

@router.get("/followed", response_model=dict)
async def get_tweets(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Роут, возвращающий все записи пользователей, на которых подписан текущий пользователь.
    """
    # Получаем ID пользователей, на которых подписан current_user
    try:
        following_ids_query = await session.execute(
            select(Follow.followed_id).where(Follow.leader_id == current_user.id)
        )
        following_ids = following_ids_query.scalars().all()

        # Получаем твиты пользователей из списка following_ids
        result = await session.execute(
            select(Tweet)
            .options(selectinload(Tweet.media))  # Загрузка медиафайлов
            .where(Tweet.author_id.in_(following_ids))
            .order_by(Tweet.created_at.desc())
        )
        tweets = result.scalars().all()

        # Форматируем данные
        tweets_data = [
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": [
                    f"/media/{media.id}" for media in tweet.media  # Генерируем относительные ссылки на медиа
                ]
            }
            for tweet in tweets
        ]

        return {"result": True, "tweets": tweets_data}

    except Exception as e:
        # Обрабатываем ошибки и возвращаем в формате, указанном в ТЗ
        return {
            "result": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }

@router.delete("/{tweet_id}/delete")
async def delete_tweet(
        tweet_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Роут для удаления твитов по id
    """
    query = await session.execute(
        select(Tweet).where(Tweet.id == tweet_id)
    )
    tweet_to_delete = query.scalar_one_or_none()
    if not tweet_to_delete:
        raise HTTPException(status_code=400, detail="No such tweet")
    if tweet_to_delete.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this tweet")

    await session.delete(tweet_to_delete)
    await session.commit()

    return {"result": True}


@router.post("/{tweet_id}/likes", response_model=dict)
async def like_tweet(
        tweet_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet_to_like = query.scalar_one_or_none()
    if not tweet_to_like:
        raise HTTPException(status_code=400, detail="No such tweet")

    like = Like(tweet_id=tweet_id, user_id=current_user.id)
    session.add(like)
    await session.commit()

    return {"result": True}


@router.delete("/{tweet_id}/likes")
async def delete_like(
        tweet_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = await session.execute(select(Like).where(Like.tweet_id == tweet_id, Like.user_id == current_user.id))
    tweet_to_unlike = query.scalar_one_or_none()
    if not tweet_to_unlike:
        raise HTTPException(status_code=400, detail="You haven't marked this like")

    await session.delete(tweet_to_unlike)
    await session.commit()

    return {"result": True}


@router.put("/{tweet_id}", response_model=TweetUpdateResponse)
async def update_tweet(
        tweet_id: int,
        tweet_update: TweetUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    query = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet_to_update = query.scalar_one_or_none()
    if not tweet_to_update:
        raise HTTPException(status_code=400, detail="No such tweet")

    if tweet_to_update.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this tweet")

    if tweet_update.content is not None:
        tweet_to_update.tweet_data = tweet_update.content
    if tweet_update.media is not None:
        tweet_to_update.media = tweet_update.media

    session.add(tweet_to_update)
    await session.commit()
    await session.refresh(tweet_to_update)

    return tweet_to_update


@router.get("/{tweet_id}", response_model=dict)
async def get_tweet_by_id(
        tweet_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Tweet)
        .options(selectinload(Tweet.media))
        .where(Tweet.id == tweet_id)
    )
    tweet_to_get = result.scalar_one_or_none()
    if not tweet_to_get:
        raise HTTPException(status_code=404, detail="Tweet not found")
    else:
        tweet = {
                "id": tweet_to_get.id,
                "content": tweet_to_get.content,
                "attachments": [
                    f"/media/{media.id}" for media in tweet_to_get.media  # Генерируем относительные ссылки на медиа
                ]
            }

    return tweet
