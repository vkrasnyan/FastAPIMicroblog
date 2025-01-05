from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from blogapp.database import Base


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = relationship('User', back_populates='tweets')
    likes = relationship('Like', back_populates='tweet')
    media = relationship('Media', back_populates='tweet')
