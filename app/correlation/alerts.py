from datetime import datetime
from app.db.models import ThreatIndicator


ALERT_THRESHOLDS = {
    "critical": 85,
    "high": 65,
    "medium": 40,
    "low": 0,
}


def generate_alert(threat: ThreatIndicator) -> dict | None:
    if threat.risk_score >= ALERT_THRESHOLDS["critical"]:
        level = "CRITICAL"
    elif threat.risk_score >= ALERT_THRESHOLDS["high"]:
        level = "HIGH"
    elif threat.risk_score >= ALERT_THRESHOLDS["medium"]:
        level = "MEDIUM"
    else:
        return None

    return {
        "alert_level": level,
        "threat_id": threat.id,
        "threat_value": threat.value,
        "threat_type": threat.type,
        "risk_score": threat.risk_score,
        "source": threat.source,
        "tags": threat.tags,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"{level}: {threat.type.upper()} {threat.value} "
                   f"(score: {threat.risk_score}) from {threat.source}",
    }