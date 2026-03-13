from sqlalchemy import Column, Integer, Text, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class FactCheck(Base):

    __tablename__ = "fact_checks"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    claim = Column(Text, nullable=False)

    similarity = Column(Float)

    verdict = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())