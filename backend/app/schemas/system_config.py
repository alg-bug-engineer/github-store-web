from pydantic import BaseModel
from typing import Optional, Dict, Any


class SystemConfigBase(BaseModel):
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(SystemConfigBase):
    pass


class SystemConfigInDBBase(SystemConfigBase):
    id: int

    class Config:
        from_attributes = True


class SystemConfig(SystemConfigInDBBase):
    pass


class SystemConfigInDB(SystemConfigInDBBase):
    pass
