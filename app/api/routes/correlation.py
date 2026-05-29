from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.correlation.engine import run_correlation
from app.db.models import ThreatIndicator
from app.correlation.mitre import map_to_mitre

router = APIRouter(prefix="/api/correlate", tags=["Correlation"])


@router.post("/run")
def correlate_all(db: Session = Depends(get_db)):
    result = run_correlation(db)
    return result


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 40
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    alerts = []
    for threat in threats:
        level = (
            "CRITICAL" if threat.risk_score >= 85 else
            "HIGH" if threat.risk_score >= 65 else
            "MEDIUM"
        )
        alerts.append({
            "level": level,
            "type": threat.type,
            "value": threat.value,
            "risk_score": threat.risk_score,
            "tags": threat.tags,
            "source": threat.source,
        })

    return {"total": len(alerts), "alerts": alerts}


@router.get("/mitre/{threat_id}")
def get_mitre_mapping(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()

    if not threat:
        return {"error": "Threat not found"}

    techniques = map_to_mitre(
        threat.description or "",
        threat.tags or ""
    )

    return {
        "threat_id": threat_id,
        "value": threat.value,
        "mitre_techniques": techniques,
    }