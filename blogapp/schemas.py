from pydantic import BaseModel


class BaseTweet(BaseModel):
    content: str
    author_id: int
