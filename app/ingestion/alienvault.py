import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.ingestion.base import save_threat

OTX_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"


def fetch_alienvault(db: Session, limit: int = 10) -> dict:
    if not settings.ALIENVAULT_API_KEY:
        print("AlienVault API key not set")
        return {"saved": 0, "skipped": 0}

    headers = {"X-OTX-API-KEY": settings.ALIENVAULT_API_KEY}
    params = {"limit": limit}

    try:
        print("Fetching AlienVault OTX pulses...")
        response = httpx.get(OTX_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        saved = 0
        skipped = 0

        for pulse in data.get("results", []):
            tags = ",".join(pulse.get("tags", []))
            description = pulse.get("description", "")

            for indicator in pulse.get("indicators", []):
                itype = indicator.get("type", "").lower()

                if itype not in ["ipv4", "domain", "url", "filehash-md5", "filehash-sha256"]:
                    continue

                type_map = {
                    "ipv4": "ip",
                    "domain": "domain",
                    "url": "url",
                    "filehash-md5": "hash",
                    "filehash-sha256": "hash",
                }

                threat_data = {
                    "type": type_map.get(itype, "unknown"),
                    "value": indicator.get("indicator"),
                    "severity": "high",
                    "confidence": 75.0,
                    "risk_score": 75.0,
                    "source": "alienvault",
                    "tags": tags,
                    "description": description[:500],
                    "country": indicator.get("country_code", ""),
                }

                if save_threat(db, threat_data):
                    saved += 1
                else:
                    skipped += 1

        print(f"AlienVault: {saved} saved, {skipped} skipped")
        return {"saved": saved, "skipped": skipped}

    except Exception as e:
        print(f"AlienVault fetch error: {e}")
        return {"saved": 0, "skipped": 0}