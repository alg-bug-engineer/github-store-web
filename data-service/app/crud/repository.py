from typing import Optional, List, Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.crud.base import CRUDBase
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate, RepositoryUpdate


class CRUDRepository(CRUDBase[Repository, RepositoryCreate, RepositoryUpdate]):
    def get_by_full_name(
        self, db: Session, *, full_name: str
    ) -> Optional[Repository]:
        return db.query(Repository).filter(Repository.full_name == full_name).first()

    def get_by_github_id(self, db: Session, *, github_id: int) -> Optional[Repository]:
        return db.query(Repository).filter(Repository.github_id == github_id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        order_by_desc: bool = True,
    ) -> List[Repository]:
        query = db.query(self.model)
        if sort_by:
            sort_column = getattr(self.model, sort_by, None)
            if sort_column is not None:
                if order_by_desc:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        return query.offset(skip).limit(limit).all()

    def get_multi_by_ids(
        self, db: Session, *, ids: List[int], skip: int = 0, limit: int = 100
    ) -> List[Repository]:
        return db.query(self.model).filter(self.model.id.in_(ids)).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: RepositoryCreate, github_data: Dict[str, Any]) -> Repository:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_obj.github_data = github_data  # Store the raw GitHub API data
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Repository,
        obj_in: Union[RepositoryUpdate, Dict[str, Any]],
        github_data: Dict[str, Any]
    ) -> Repository:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_obj.github_data = github_data  # Store the raw GitHub API data

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


repository = CRUDRepository(Repository)
