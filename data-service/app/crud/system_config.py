from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class CRUDSystemConfig(CRUDBase[SystemConfig, SystemConfigCreate, SystemConfigUpdate]):
    def get_by_key(self, db: Session, *, key: str) -> Optional[SystemConfig]:
        return db.query(SystemConfig).filter(SystemConfig.key == key).first()


system_config = CRUDSystemConfig(SystemConfig)
