from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from blogapp.database import Base


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    user = relationship('User')
    tweet = relationship('Tweet', back_populates='likes')