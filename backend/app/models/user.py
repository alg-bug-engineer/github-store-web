from sqlalchemy import Column, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar_url = Column(String(255))
    status = Column(SmallInteger, default=1, index=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
