from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.core.alerting import send_critical_threat_alert, send_slack_alert, send_email_alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


class TestAlertRequest(BaseModel):
    message: str = "Test alert from ThreatLens"


@router.post("/test-slack")
def test_slack(request: TestAlertRequest):
    result = send_slack_alert(request.message)
    return {"sent": result}


@router.post("/test-email")
def test_email(request: TestAlertRequest):
    result = send_email_alert("ThreatLens Test Alert", request.message)
    return {"sent": result}


@router.post("/alert-critical")
def alert_critical_threats(db: Session = Depends(get_db)):
    critical_threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 85
    ).order_by(ThreatIndicator.risk_score.desc()).limit(5).all()

    if not critical_threats:
        raise HTTPException(status_code=404, detail="No critical threats found")

    results = []
    for threat in critical_threats:
        result = send_critical_threat_alert(threat)
        results.append(result)

    return {"alerts_sent": len(results), "results": results}


@router.get("/critical")
def get_critical_threats(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 85
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    return {
        "total": len(threats),
        "threats": [
            {
                "id": t.id,
                "value": t.value,
                "type": t.type,
                "risk_score": t.risk_score,
                "source": t.source,
                "tags": t.tags,
            }
            for t in threats
        ]
    }