from sqlalchemy import Column, Integer, String, ForeignKey,DateTime, func
from sqlalchemy.orm import relationship
from blogapp.database import Base


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = relationship('User', back_populates='tweets', lazy='dynamic')
    likes = relationship('Like', back_populates='tweet', lazy='dynamic')
    media = relationship('Media', back_populates='tweet', lazy='dynamic')
