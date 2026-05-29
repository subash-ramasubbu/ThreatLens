from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import ThreatIndicator


def save_threat(db: Session, data: dict) -> bool:
    try:
        existing = db.query(ThreatIndicator).filter(
            ThreatIndicator.value == data["value"]
        ).first()

        if existing:
            existing.last_seen = datetime.utcnow()
            existing.confidence = max(existing.confidence, data.get("confidence", 0))
            db.commit()
            return False

        threat = ThreatIndicator(
            type=data.get("type", "ip"),
            value=data["value"],
            severity=data.get("severity", "medium"),
            confidence=data.get("confidence", 0.0),
            risk_score=data.get("risk_score", 0.0),
            source=data.get("source", "unknown"),
            tags=data.get("tags", ""),
            description=data.get("description", ""),
            country=data.get("country", ""),
        )
        db.add(threat)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"Error saving threat: {e}")
        return False