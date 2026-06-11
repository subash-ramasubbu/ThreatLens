from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.threat_hunting import (
    hunt_by_tag,
    hunt_by_mitre,
    hunt_high_risk_ips,
    hunt_c2_infrastructure,
)

router = APIRouter(prefix="/api/hunt", tags=["Threat Hunting"])


@router.get("/tag/{tag}")
def hunt_tag(tag: str, db: Session = Depends(get_db)):
    return hunt_by_tag(tag, db)


@router.get("/mitre/{technique_id}")
def hunt_mitre(technique_id: str, db: Session = Depends(get_db)):
    return hunt_by_mitre(technique_id, db)


@router.get("/high-risk-ips")
def high_risk_ips(db: Session = Depends(get_db)):
    return hunt_high_risk_ips(db)


@router.get("/c2-infrastructure")
def c2_infrastructure(db: Session = Depends(get_db)):
    return hunt_c2_infrastructure(db)