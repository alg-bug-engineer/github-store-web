from sqlalchemy import Column, DateTime, BigInteger, Text, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from app.db.base_class import Base


class Recommendation(Base):
    id = Column(BigInteger, primary_key=True, index=True)

    # Recommendation Type
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Recommendation Content
    repo_ids = Column(ARRAY(BigInteger))
    display_order = Column(Integer, default=0, index=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    start_at = Column(DateTime)
    end_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
