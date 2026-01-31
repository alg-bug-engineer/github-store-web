from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.readme_cache import ReadmeCache
from app.schemas.readme_cache import ReadmeCacheCreate, ReadmeCacheUpdate


class CRUDReadmeCache(CRUDBase[ReadmeCache, ReadmeCacheCreate, ReadmeCacheUpdate]):
    def get_by_repo_id(self, db: Session, *, repo_id: int) -> Optional[ReadmeCache]:
        return db.query(ReadmeCache).filter(ReadmeCache.repo_id == repo_id).first()


readme_cache = CRUDReadmeCache(ReadmeCache)
