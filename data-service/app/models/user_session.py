from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class UserSession(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, index=True)
    token = Column(String(64), unique=True, index=True, nullable=False)
    device_info = Column(JSON)
    ip_address = Column(String(45))
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
