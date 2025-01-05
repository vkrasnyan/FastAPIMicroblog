from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from blogapp.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)

    tweets = relationship("Tweet", back_populates="author")

    # Связь с пользователями, на которых этот пользователь подписан
    follow_up = relationship("Follow", foreign_keys="[Follow.leader_id]", back_populates="leader")

    # Связь с пользователями, которые подписаны на этого пользователя
    follow_down = relationship("Follow", foreign_keys="[Follow.followed_id]", back_populates="followed")
