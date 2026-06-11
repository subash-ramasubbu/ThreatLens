import httpx


def lookup_cve(cve_id: str) -> dict:
    try:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0"
        params = {"keywordSearch": cve_id}
        response = httpx.get(url, params=params, timeout=15)
        data = response.json()

        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            return {"error": f"CVE {cve_id} not found"}

        cve = vulnerabilities[0].get("cve", {})

        descriptions = cve.get("descriptions", [])
        description = next(
            (d["value"] for d in descriptions if d["lang"] == "en"), ""
        )

        metrics = cve.get("metrics", {})
        cvss_score = 0.0
        severity = "unknown"
        vector = ""

        if "cvssMetricV31" in metrics:
            cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
            cvss_score = cvss_data.get("baseScore", 0.0)
            severity = cvss_data.get("baseSeverity", "unknown")
            vector = cvss_data.get("vectorString", "")
        elif "cvssMetricV2" in metrics:
            cvss_data = metrics["cvssMetricV2"][0]["cvssData"]
            cvss_score = cvss_data.get("baseScore", 0.0)
            vector = cvss_data.get("vectorString", "")

        references = [
            ref.get("url", "")
            for ref in cve.get("references", [])[:5]
        ]

        weaknesses = []
        for weakness in cve.get("weaknesses", []):
            for desc in weakness.get("description", []):
                if desc.get("lang") == "en":
                    weaknesses.append(desc.get("value", ""))

        return {
            "cve_id": cve.get("id", cve_id),
            "description": description[:500],
            "cvss_score": cvss_score,
            "severity": severity.lower(),
            "vector_string": vector,
            "weaknesses": weaknesses[:3],
            "references": references,
            "published": cve.get("published", ""),
            "last_modified": cve.get("lastModified", ""),
        }

    except Exception as e:
        return {"error": str(e)}