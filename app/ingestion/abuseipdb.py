import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.ingestion.base import save_threat

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/blacklist"


def fetch_abuseipdb(db: Session, limit: int = 100) -> dict:
    if not settings.ABUSEIPDB_API_KEY:
        print("AbuseIPDB API key not set")
        return {"saved": 0, "skipped": 0}

    headers = {
        "Key": settings.ABUSEIPDB_API_KEY,
        "Accept": "application/json",
    }
    params = {
        "confidenceMinimum": 90,
        "limit": limit,
    }

    try:
        print("Fetching AbuseIPDB blacklist...")
        response = httpx.get(ABUSEIPDB_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        saved = 0
        skipped = 0

        for entry in data.get("data", []):
            confidence = entry.get("abuseConfidenceScore", 0)
            severity = "critical" if confidence >= 90 else "high" if confidence >= 70 else "medium"

            threat_data = {
                "type": "ip",
                "value": entry.get("ipAddress"),
                "severity": severity,
                "confidence": float(confidence),
                "risk_score": float(confidence),
                "source": "abuseipdb",
                "tags": "malicious-ip",
                "description": f"Reported {entry.get('totalReports', 0)} times. Last reported: {entry.get('lastReportedAt', '')}",
                "country": entry.get("countryCode", ""),
            }

            if save_threat(db, threat_data):
                saved += 1
            else:
                skipped += 1

        print(f"AbuseIPDB: {saved} saved, {skipped} skipped")
        return {"saved": saved, "skipped": skipped}

    except Exception as e:
        print(f"AbuseIPDB fetch error: {e}")
        return {"saved": 0, "skipped": 0}