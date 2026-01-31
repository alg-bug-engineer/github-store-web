from sqlalchemy import Column, DateTime, BigInteger, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ReadmeCache(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    repo_id = Column(BigInteger, ForeignKey("repository.id"), unique=True, nullable=False)

    # README Content
    content = Column(Text)
    html_content = Column(Text)
    encoding = Column(String(20))

    # Timestamps
    synced_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    repository = relationship("Repository")
