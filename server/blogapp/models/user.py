from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from blogapp.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tweets = relationship("Tweet", back_populates="author", lazy="dynamic")
    likes = relationship("Like", back_populates="user", lazy="dynamic")
    follow_up = relationship("Follow", foreign_keys="[Follow.leader_id]", back_populates="leader")
    follow_down = relationship("Follow", foreign_keys="[Follow.followed_id]", back_populates="followed")

