from sqlalchemy.orm import Session
from app.db.models import ThreatIndicator


def hunt_by_tag(tag: str, db: Session) -> dict:
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.tags.contains(tag)
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    return {
        "hunt_query": f"tag:{tag}",
        "results": len(threats),
        "threats": [
            {
                "id": t.id,
                "value": t.value,
                "type": t.type,
                "risk_score": t.risk_score,
                "tags": t.tags,
                "source": t.source,
            }
            for t in threats[:20]
        ]
    }


def hunt_by_mitre(technique_id: str, db: Session) -> dict:
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.tags.contains(technique_id)
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    return {
        "hunt_query": f"mitre:{technique_id}",
        "technique_id": technique_id,
        "results": len(threats),
        "threats": [
            {
                "id": t.id,
                "value": t.value,
                "type": t.type,
                "risk_score": t.risk_score,
                "tags": t.tags,
            }
            for t in threats[:20]
        ]
    }


def hunt_high_risk_ips(db: Session) -> dict:
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.type == "ip",
        ThreatIndicator.risk_score >= 85,
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    return {
        "hunt_query": "high-risk-ips",
        "results": len(threats),
        "threats": [
            {
                "id": t.id,
                "value": t.value,
                "risk_score": t.risk_score,
                "country": t.country,
                "tags": t.tags,
                "source": t.source,
            }
            for t in threats[:20]
        ]
    }


def hunt_c2_infrastructure(db: Session) -> dict:
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.tags.contains("c2")
    ).order_by(ThreatIndicator.risk_score.desc()).all()

    return {
        "hunt_query": "c2-infrastructure",
        "results": len(threats),
        "threats": [
            {
                "id": t.id,
                "value": t.value,
                "type": t.type,
                "risk_score": t.risk_score,
                "tags": t.tags,
            }
            for t in threats[:20]
        ]
    }