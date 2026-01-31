from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user_favorite import UserFavorite
from app.schemas.user_favorite import UserFavoriteCreate, UserFavoriteUpdate


class CRUDUserFavorite(CRUDBase[UserFavorite, UserFavoriteCreate, UserFavoriteUpdate]):
    def get_by_user_id_and_repo_id(
        self, db: Session, *, user_id: int, repo_id: int
    ) -> Optional[UserFavorite]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.repo_id == repo_id)
            .first()
        )

    def get_multi_by_user_id(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserFavorite]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


user_favorite = CRUDUserFavorite(UserFavorite)
