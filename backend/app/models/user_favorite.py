from sqlalchemy import Column, DateTime, BigInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class UserFavorite(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    repo_id = Column(BigInteger, ForeignKey("repository.id"), nullable=False, index=True)

    # Favorite Info
    note = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User")
    repository = relationship("Repository")

    __table_args__ = (UniqueConstraint("user_id", "repo_id", name="user_repo_favorite_uc"),)
