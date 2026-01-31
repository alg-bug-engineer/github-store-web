from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.release import Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate


class CRUDRelease(CRUDBase[Release, ReleaseCreate, ReleaseUpdate]):
    def get_by_github_release_id(
        self, db: Session, *, github_release_id: int
    ) -> Optional[Release]:
        return (
            db.query(self.model)
            .filter(self.model.github_release_id == github_release_id)
            .first()
        )

    def get_latest_release_by_repo_id(
        self, db: Session, *, repo_id: int
    ) -> Optional[Release]:
        return (
            db.query(self.model)
            .filter(self.model.repo_id == repo_id, self.model.is_latest == True)
            .order_by(self.model.published_at.desc())
            .first()
        )

    def get_multi_by_repo_id(
        self, db: Session, *, repo_id: int, skip: int = 0, limit: int = 100
    ) -> List[Release]:
        return (
            db.query(self.model)
            .filter(self.model.repo_id == repo_id)
            .order_by(self.model.published_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


release = CRUDRelease(Release)
