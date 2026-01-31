from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate


class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
    def get_by_type(
        self, db: Session, *, type: str, skip: int = 0, limit: int = 100
    ) -> List[Recommendation]:
        return (
            db.query(self.model)
            .filter(self.model.type == type, self.model.is_active == True)
            .order_by(self.model.display_order)
            .offset(skip)
            .limit(limit)
            .all()
        )


recommendation = CRUDRecommendation(Recommendation)
