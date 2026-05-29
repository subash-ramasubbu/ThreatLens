from app.db.models import ThreatIndicator


def calculate_risk_score(threat: ThreatIndicator) -> float:
    score = 0.0

    # Base score from confidence
    score += threat.confidence * 0.4

    # Severity weight
    severity_weights = {
        "critical": 40,
        "high": 30,
        "medium": 20,
        "low": 10,
    }
    score += severity_weights.get(threat.severity.lower(), 20)

    # Source reliability weight
    source_weights = {
        "nvd": 15,
        "abuseipdb": 12,
        "alienvault": 10,
        "misp": 13,
    }
    score += source_weights.get(threat.source.lower(), 8)

    # Tag-based bonus
    high_risk_tags = [
        "ransomware", "c2", "apt", "exploit",
        "malware", "backdoor", "rootkit"
    ]
    threat_tags = threat.tags.lower() if threat.tags else ""
    for tag in high_risk_tags:
        if tag in threat_tags:
            score += 5

    return min(round(score, 2), 100.0)