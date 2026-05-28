from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ThreatCreate(BaseModel):
    type: str
    value: str
    severity: Optional[str] = "medium"
    confidence: Optional[float] = 0.0
    source: str
    tags: Optional[str] = ""
    description: Optional[str] = ""
    country: Optional[str] = ""

class ThreatResponse(BaseModel):
    id: int
    type: str
    value: str
    severity: str
    confidence: float
    risk_score: float
    source: str
    tags: str
    description: str
    country: str
    first_seen: datetime
    last_seen: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ThreatUpdate(BaseModel):
    severity: Optional[str] = None
    confidence: Optional[float] = None
    risk_score: Optional[float] = None
    tags: Optional[str] = None
    description: Optional[str] = None