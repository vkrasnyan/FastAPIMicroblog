from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Схемы для пользователей
class UserBase(BaseModel):
    name: str = Field(..., title="User's name", max_length=100)

class UserCreate(UserBase):
    api_key: str = Field(..., title="API Key for user authentication", min_length=8)

class UserResponse(UserBase):
    id: int
    created_at: datetime = Field(..., title="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, title="Last update timestamp")

    class Config:
        orm_mode = True

class UserUpdate(UserBase):
    name: Optional[str] = None


# Схемы для твитов
class TweetBase(BaseModel):
    content: str

class TweetCreate(TweetBase):
    pass

class TweetResponse(TweetBase):
    id: int
    author_id: int
    updated_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


# Схемы для подписок (follows)
class FollowBase(BaseModel):
    leader_id: int
    followed_id: int


class FollowCreate(FollowBase):
    pass


class FollowResponse(FollowBase):
    id: int
    leader_id: int
    followed_id: int

    class Config:
        orm_mode = True


# Схемы для лайков
class LikeBase(BaseModel):
    tweet_id: int
    user_id: int


class LikeCreate(LikeBase):
    pass


class LikeResponse(LikeBase):
    id: int
    tweet_id: int
    user_id: int

    class Config:
        orm_mode = True


# Схемы для медиа
class MediaBase(BaseModel):
    file_path: str
    tweet_id: int

class MediaCreate(MediaBase):
    pass

class MediaResponse(MediaBase):
    id: int
    tweet_id: int
    created_at: datetime

    class Config:
        orm_mode = True
