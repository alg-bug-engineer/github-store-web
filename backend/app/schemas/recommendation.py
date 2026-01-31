from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecommendationBase(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    repo_ids: Optional[List[int]] = None
    display_order: int = 0
    is_active: bool = True
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(RecommendationBase):
    pass


class RecommendationInDBBase(RecommendationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Recommendation(RecommendationInDBBase):
    pass


class RecommendationInDB(RecommendationInDBBase):
    pass
