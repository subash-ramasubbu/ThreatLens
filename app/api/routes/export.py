from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.core.stix_export import export_bundle, threat_to_stix
from app.core.pdf_report import generate_pdf_report

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/stix2")
def export_stix2(
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ThreatIndicator)
    if severity:
        query = query.filter(ThreatIndicator.severity == severity)
    threats = query.order_by(
        ThreatIndicator.risk_score.desc()
    ).limit(limit).all()
    if not threats:
        raise HTTPException(status_code=404, detail="No threats found")
    bundle = export_bundle(threats)
    return JSONResponse(
        content=bundle,
        headers={"Content-Disposition": "attachment; filename=threatlens-export.json"}
    )


@router.get("/stix2/{threat_id}")
def export_single_stix2(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    stix_obj = threat_to_stix(threat)
    if not stix_obj:
        raise HTTPException(status_code=500, detail="Failed to convert threat to STIX2")
    return JSONResponse(content=stix_obj)


@router.get("/summary")
def export_summary(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).all()
    if not threats:
        raise HTTPException(status_code=404, detail="No threats found")

    from collections import Counter
    all_tags = []
    for t in threats:
        if t.tags:
            all_tags.extend(t.tags.split(","))

    return {
        "total_indicators": len(threats),
        "by_type": dict(Counter(t.type for t in threats)),
        "by_severity": dict(Counter(t.severity for t in threats)),
        "by_source": dict(Counter(t.source for t in threats)),
        "top_tags": dict(Counter(all_tags).most_common(10)),
        "avg_risk_score": round(sum(t.risk_score for t in threats) / len(threats), 2),
        "critical_count": len([t for t in threats if t.risk_score >= 85]),
        "export_format": "STIX2.1",
    }


@router.get("/pdf")
def export_pdf(db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).order_by(
        ThreatIndicator.risk_score.desc()
    ).limit(50).all()
    if not threats:
        raise HTTPException(status_code=404, detail="No threats found")

    from collections import Counter
    summary = {
        "total": len(threats),
        "critical": len([t for t in threats if t.risk_score >= 85]),
        "high": len([t for t in threats if 65 <= t.risk_score < 85]),
        "medium": len([t for t in threats if 40 <= t.risk_score < 65]),
        "avg_risk_score": round(sum(t.risk_score for t in threats) / len(threats), 2),
    }
    threats_list = [
        {
            "value": t.value,
            "type": t.type,
            "risk_score": t.risk_score,
            "source": t.source,
            "tags": t.tags,
        }
        for t in threats
    ]
    pdf_bytes = generate_pdf_report(summary, threats_list)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=threatlens-report.pdf"}
    )