from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from blogapp.database import Base


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_body = Column(LargeBinary)
    file_name = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=True)
    tweet = relationship('Tweet', back_populates='media')
