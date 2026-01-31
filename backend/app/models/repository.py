from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, BigInteger, Text, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class Repository(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String(255), unique=True, index=True, nullable=False)
    owner = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    homepage = Column(String(255))

    # GitHub Data
    github_id = Column(BigInteger, unique=True)
    html_url = Column(String(255))
    avatar_url = Column(String(255))

    # Statistics
    stars = Column(Integer, default=0, index=True)
    forks = Column(Integer, default=0)
    watchers = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    # New Field
    total_downloads = Column(Integer, default=0)

    # Classification
    language = Column(String(50), index=True)
    topics = Column(ARRAY(Text))
    # New Field
    detected_platforms = Column(ARRAY(String), default=[])  # ['windows', 'mac', 'linux']
    category = Column(String(50), index=True)
    # New Field
    primary_category = Column(String(50), nullable=True)  # 'productivity', 'developer_tools', etc.

    # Status
    has_releases = Column(Boolean, default=False, index=True)
    # New Fields
    latest_version = Column(String(50), nullable=True)  # 'v2.3.0'
    latest_release_date = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)

    # Raw API Data
    github_data = Column(JSONB)

    # Update Strategy
    update_priority = Column(SmallInteger, default=2, index=True)
    next_update_at = Column(DateTime, index=True)

    # Timestamps
    github_created_at = Column(DateTime)
    github_updated_at = Column(DateTime)
    last_synced_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
