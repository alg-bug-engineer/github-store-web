from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RepositoryBase(BaseModel):
    full_name: str
    owner: str
    name: str
    description: Optional[str] = None
    homepage: Optional[str] = None
    github_id: int
    html_url: str
    avatar_url: str
    stars: int
    forks: int
    watchers: int
    open_issues: int
    total_downloads: int = 0
    language: Optional[str] = None
    topics: Optional[List[str]] = []
    detected_platforms: Optional[List[str]] = []
    category: Optional[str] = None
    primary_category: Optional[str] = None
    has_releases: bool
    latest_version: Optional[str] = None
    latest_release_date: Optional[datetime] = None
    is_archived: bool
    is_active: bool
    update_priority: int
    next_update_at: Optional[datetime] = None
    github_created_at: Optional[datetime] = None
    github_updated_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryUpdate(RepositoryBase):
    pass


class RepositoryInDBBase(RepositoryBase):
    id: int

    class Config:
        from_attributes = True


class Repository(RepositoryInDBBase):
    pass


class RepositoryInDB(RepositoryInDBBase):
    pass
