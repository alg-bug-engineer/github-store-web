from sqlalchemy import Column, DateTime, BigInteger, Text, Integer, JSON, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class SearchHistory(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), index=True)  # Can be NULL for guest users

    # Search Info
    query = Column(Text, nullable=False, index=True)
    filters = Column(JSON)
    result_count = Column(Integer)

    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User")
