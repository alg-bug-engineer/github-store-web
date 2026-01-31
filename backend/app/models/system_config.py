from sqlalchemy import Column, DateTime, BigInteger, Text, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base


class SystemConfig(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
