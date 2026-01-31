from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.phone == phone).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            phone=obj_in.phone,
            nickname=obj_in.nickname,
            password_hash=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
