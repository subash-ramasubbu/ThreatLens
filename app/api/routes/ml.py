from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.core.ml_detector import detect_anomalies

router = APIRouter(prefix="/api/ml", tags=["ML Detection"])


@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).all()
    if not threats:
        raise HTTPException(status_code=404, detail="No threats found")
    return detect_anomalies(threats)


@router.get("/anomalies/critical")
def get_critical_anomalies(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 70
    ).all()
    if not threats:
        raise HTTPException(status_code=404, detail="No threats found")
    result = detect_anomalies(threats)
    if "top_anomalies" in result:
        result["top_anomalies"] = [
            a for a in result["top_anomalies"]
            if a["risk_score"] >= 85
        ]
    return result