from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Release(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    repo_id = Column(BigInteger, ForeignKey("repository.id"), nullable=False, index=True)

    # Release Info
    github_release_id = Column(BigInteger, unique=True)
    tag_name = Column(String(100), nullable=False, index=True)
    name = Column(String(255))
    body = Column(Text)

    # Version Status
    is_prerelease = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    is_latest = Column(Boolean, default=False, index=True)

    # Timestamps
    published_at = Column(DateTime, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    repository = relationship("Repository")
