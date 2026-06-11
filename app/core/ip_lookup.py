import httpx
from app.core.config import settings
from app.db.models import ThreatIndicator
from sqlalchemy.orm import Session


def lookup_ip_abuseipdb(ip: str) -> dict:
    if not settings.ABUSEIPDB_API_KEY:
        return {"error": "API key not configured"}
    try:
        headers = {"Key": settings.ABUSEIPDB_API_KEY, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90, "verbose": True}
        response = httpx.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers=headers,
            params=params,
            timeout=10,
        )
        data = response.json().get("data", {})
        return {
            "ip": ip,
            "abuse_confidence": data.get("abuseConfidenceScore", 0),
            "country": data.get("countryCode", ""),
            "isp": data.get("isp", ""),
            "domain": data.get("domain", ""),
            "total_reports": data.get("totalReports", 0),
            "last_reported": data.get("lastReportedAt", ""),
            "is_tor": data.get("isTor", False),
            "is_public": data.get("isPublic", True),
        }
    except Exception as e:
        return {"error": str(e)}


def lookup_ip_local(ip: str, db: Session) -> dict:
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.value == ip
    ).first()

    if threat:
        return {
            "found_locally": True,
            "id": threat.id,
            "severity": threat.severity,
            "risk_score": threat.risk_score,
            "tags": threat.tags,
            "source": threat.source,
            "description": threat.description,
            "first_seen": str(threat.first_seen),
            "last_seen": str(threat.last_seen),
        }
    return {"found_locally": False}


def full_ip_lookup(ip: str, db: Session) -> dict:
    local = lookup_ip_local(ip, db)
    external = lookup_ip_abuseipdb(ip)

    verdict = "unknown"
    if local.get("found_locally"):
        score = local.get("risk_score", 0)
        if score >= 85:
            verdict = "CRITICAL"
        elif score >= 65:
            verdict = "HIGH"
        elif score >= 40:
            verdict = "MEDIUM"
        else:
            verdict = "LOW"
    elif external.get("abuse_confidence", 0) >= 50:
        verdict = "SUSPICIOUS"

    return {
        "ip": ip,
        "verdict": verdict,
        "local_intel": local,
        "external_intel": external,
    }