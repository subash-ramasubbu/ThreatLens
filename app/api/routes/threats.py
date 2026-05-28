from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.api.schemas import ThreatCreate, ThreatResponse, ThreatUpdate

router = APIRouter(prefix="/api/threats", tags=["Threats"])


@router.post("/", response_model=ThreatResponse)
def create_threat(threat: ThreatCreate, db: Session = Depends(get_db)):
    existing = db.query(ThreatIndicator).filter(
        ThreatIndicator.value == threat.value
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Threat indicator already exists")
    
    db_threat = ThreatIndicator(**threat.dict())
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat


@router.get("/", response_model=List[ThreatResponse])
def get_all_threats(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ThreatIndicator)
    if severity:
        query = query.filter(ThreatIndicator.severity == severity)
    return query.offset(skip).limit(limit).all()


@router.get("/search", response_model=List[ThreatResponse])
def search_threats(q: str, db: Session = Depends(get_db)):
    results = db.query(ThreatIndicator).filter(
        ThreatIndicator.value.contains(q) |
        ThreatIndicator.tags.contains(q) |
        ThreatIndicator.description.contains(q)
    ).all()
    if not results:
        raise HTTPException(status_code=404, detail="No threats found")
    return results


@router.get("/{threat_id}", response_model=ThreatResponse)
def get_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat


@router.patch("/{threat_id}", response_model=ThreatResponse)
def update_threat(
    threat_id: int,
    updates: ThreatUpdate,
    db: Session = Depends(get_db)
):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    for field, value in updates.dict(exclude_none=True).items():
        setattr(threat, field, value)
    
    db.commit()
    db.refresh(threat)
    return threat


@router.delete("/{threat_id}")
def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    db.delete(threat)
    db.commit()
    return {"message": f"Threat {threat_id} deleted successfully"}