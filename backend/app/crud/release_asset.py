from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.release_asset import ReleaseAsset
from app.schemas.release_asset import ReleaseAssetCreate, ReleaseAssetUpdate


class CRUDReleaseAsset(CRUDBase[ReleaseAsset, ReleaseAssetCreate, ReleaseAssetUpdate]):
    def get_by_github_asset_id(
        self, db: Session, *, github_asset_id: int
    ) -> Optional[ReleaseAsset]:
        return (
            db.query(self.model)
            .filter(self.model.github_asset_id == github_asset_id)
            .first()
        )

    def get_multi_by_release_id(
        self, db: Session, *, release_id: int, skip: int = 0, limit: int = 100
    ) -> List[ReleaseAsset]:
        return (
            db.query(self.model)
            .filter(self.model.release_id == release_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


release_asset = CRUDReleaseAsset(ReleaseAsset)
