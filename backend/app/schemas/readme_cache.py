from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReadmeCacheBase(BaseModel):
    repo_id: int
    content: Optional[str] = None
    html_content: Optional[str] = None
    encoding: Optional[str] = None
    synced_at: Optional[datetime] = None


class ReadmeCacheCreate(ReadmeCacheBase):
    pass


class ReadmeCacheUpdate(ReadmeCacheBase):
    pass


class ReadmeCacheInDBBase(ReadmeCacheBase):
    id: int

    class Config:
        from_attributes = True


class ReadmeCache(ReadmeCacheInDBBase):
    pass
