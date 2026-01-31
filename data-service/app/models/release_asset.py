from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ReleaseAsset(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    release_id = Column(BigInteger, ForeignKey("release.id"), nullable=False, index=True)

    # File Info
    github_asset_id = Column(BigInteger, unique=True)
    name = Column(String(255), nullable=False, index=True)
    label = Column(String(255))
    content_type = Column(String(100))
    size = Column(BigInteger)

    # Download Info
    browser_download_url = Column(Text, nullable=False)
    download_count = Column(Integer, default=0)

    # File Classification
    platform = Column(String(50), index=True)
    file_type = Column(String(20), index=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    release = relationship("Release")
