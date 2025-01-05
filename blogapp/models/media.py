from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from blogapp.database import Base


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_path = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    tweet = relationship('Tweet', back_populates='media')
