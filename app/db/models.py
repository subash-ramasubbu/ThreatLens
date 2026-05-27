from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)
    
    type = Column(String, nullable=False)
    value = Column(String, nullable=False, unique=True)
    severity = Column(String, default="medium")
    confidence = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    
    source = Column(String, nullable=False)
    tags = Column(Text, default="")
    description = Column(Text, default="")
    
    country = Column(String, default="")
    
    first_seen = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())