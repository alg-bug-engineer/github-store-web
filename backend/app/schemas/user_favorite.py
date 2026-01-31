from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schemas.repository import Repository


class UserFavoriteBase(BaseModel):
    user_id: int
    repo_id: int
    note: Optional[str] = None


class UserFavoriteCreate(UserFavoriteBase):
    pass


class UserFavoriteUpdate(UserFavoriteBase):
    pass


class UserFavoriteInDBBase(UserFavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserFavorite(UserFavoriteInDBBase):
    pass


class UserFavoriteInDB(UserFavoriteInDBBase):
    pass


class UserFavoriteWithRepo(UserFavoriteInDBBase):
    """UserFavorite with repository data included"""
    repository: Repository
