import httpx
from sqlalchemy.orm import Session
from app.ingestion.base import save_threat

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_nvd_cves(db: Session, limit: int = 20) -> dict:
    params = {
        "resultsPerPage": limit,
        "startIndex": 0,
    }

    try:
        print("Fetching NVD CVEs...")
        response = httpx.get(NVD_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        saved = 0
        skipped = 0

        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            cve_id = cve.get("id", "")

            descriptions = cve.get("descriptions", [])
            description = next(
                (d["value"] for d in descriptions if d["lang"] == "en"), ""
            )

            metrics = cve.get("metrics", {})
            cvss_score = 0.0
            severity = "medium"

            if "cvssMetricV31" in metrics:
                cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
                cvss_score = cvss_data.get("baseScore", 0.0)
                severity = cvss_data.get("baseSeverity", "MEDIUM").lower()
            elif "cvssMetricV2" in metrics:
                cvss_data = metrics["cvssMetricV2"][0]["cvssData"]
                cvss_score = cvss_data.get("baseScore", 0.0)

            threat_data = {
                "type": "cve",
                "value": cve_id,
                "severity": severity,
                "confidence": 100.0,
                "risk_score": cvss_score * 10,
                "source": "nvd",
                "tags": "cve,vulnerability",
                "description": description[:500],
                "country": "",
            }

            if save_threat(db, threat_data):
                saved += 1
            else:
                skipped += 1

        print(f"NVD: {saved} saved, {skipped} skipped")
        return {"saved": saved, "skipped": skipped}

    except Exception as e:
        print(f"NVD fetch error: {e}")
        return {"saved": 0, "skipped": 0}