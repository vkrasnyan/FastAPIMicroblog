from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from server.blogapp.database import Base


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Связь с пользователем, который подписан на юзера
    leader = relationship("User", foreign_keys=[leader_id], back_populates="follow_up")
    # Связь с пользователем, за которым следит юзер
    followed = relationship("User", foreign_keys=[followed_id], back_populates="follow_down")
