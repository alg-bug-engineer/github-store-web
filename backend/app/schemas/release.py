from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReleaseBase(BaseModel):
    repo_id: int
    github_release_id: Optional[int] = None
    tag_name: str
    name: Optional[str] = None
    body: Optional[str] = None
    is_prerelease: bool = False
    is_draft: bool = False
    is_latest: bool = False
    published_at: Optional[datetime] = None


class ReleaseCreate(ReleaseBase):
    pass


class ReleaseUpdate(ReleaseBase):
    pass


class ReleaseInDBBase(ReleaseBase):
    id: int

    class Config:
        from_attributes = True


class Release(ReleaseInDBBase):
    pass


class ReleaseInDB(ReleaseInDBBase):
    pass
