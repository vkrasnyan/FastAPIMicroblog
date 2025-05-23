from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# Схемы для пользователей
class UserBase(BaseModel):
    name: str = Field(..., title="User's name", max_length=100)

class UserCreate(UserBase):
    api_key: str = Field(..., title="API Key for user authentication")


class FollowerFollowingResponse(BaseModel):
    id: int
    name: str


class UserResponse(UserBase):
    id: int
    name: str
    api_key: str
    created_at: datetime = Field(..., title="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, title="Last update timestamp")
    followers: Optional[List[FollowerFollowingResponse]] = []
    following: Optional[List[FollowerFollowingResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    name: Optional[str] = None


# Схемы для твитов
class TweetBase(BaseModel):
    tweet_data: str

class TweetCreate(TweetBase):
    tweet_media_ids: Optional[List[int]] = []  # Список ID медиафайлов, привязанных к твиту

class TweetCreateResponse(BaseModel):
    result: bool
    tweet_id: int

class TweetResponse(TweetBase):
    id: int
    author_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    attachments: Optional[List[str]] = [] # Список ссылок на медиафайлы

    model_config = ConfigDict(from_attributes=True)


class TweetUpdateResponse(TweetBase):
    id: int
    author_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class TweetUpdate(BaseModel):
    content: Optional[str] = None
    media: Optional[List[int]] = None


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

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


# Схемы для медиа
class MediaBase(BaseModel):
    file_name: str
    tweet_id: int

class MediaCreate(MediaBase):
    file_body: bytes  # binary data for the file

    model_config = ConfigDict(from_attributes=True)

class MediaResponse(MediaBase):
    id: int
    tweet_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
