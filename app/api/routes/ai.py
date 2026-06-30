from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.ai.analyst import analyze_threat, analyze_custom_indicator
from app.ai.report import generate_threat_report

router = APIRouter(prefix="/api/ai", tags=["AI Analyst"])


class IndicatorRequest(BaseModel):
    indicator: str
    type: str = "ip"


@router.get("/analyze/{threat_id}")
def analyze_existing_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()

    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    return analyze_threat(threat)


@router.post("/analyze")
def analyze_indicator(request: IndicatorRequest, db: Session = Depends(get_db)):
    existing = db.query(ThreatIndicator).filter(
        ThreatIndicator.value == request.indicator
    ).first()

    if existing:
        result = analyze_threat(existing)
        result["indicator"] = existing.value
        return result

    return analyze_custom_indicator(request.indicator, request.type)


@router.get("/report")
def get_threat_report(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).all()

    if not threats:
        raise HTTPException(status_code=404, detail="No threats in database")

    from collections import Counter

    sources = Counter(t.source for t in threats)
    all_tags = []
    for t in threats:
        if t.tags:
            all_tags.extend(t.tags.split(","))
    top_tags = Counter(all_tags).most_common(10)

    critical = [t for t in threats if t.risk_score >= 85]
    samples = [
        {
            "value": t.value,
            "type": t.type,
            "risk_score": t.risk_score,
            "tags": t.tags,
        }
        for t in sorted(threats, key=lambda x: x.risk_score, reverse=True)[:5]
    ]

    summary = {
        "total": len(threats),
        "critical": len([t for t in threats if t.risk_score >= 85]),
        "high": len([t for t in threats if 65 <= t.risk_score < 85]),
        "medium": len([t for t in threats if 40 <= t.risk_score < 65]),
        "sources": dict(sources.most_common(5)),
        "tags": dict(top_tags),
        "samples": samples,
    }

    return generate_threat_report(summary)