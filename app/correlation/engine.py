from sqlalchemy.orm import Session
from app.db.models import ThreatIndicator
from app.correlation.scoring import calculate_risk_score
from app.correlation.tagger import generate_tags
from app.correlation.mitre import map_to_mitre, format_mitre_tags
from app.correlation.alerts import generate_alert


def run_correlation(db: Session) -> dict:
    threats = db.query(ThreatIndicator).all()

    alerts = []
    processed = 0

    for threat in threats:
        # Step 1: Generate enriched tags
        enriched_tags = generate_tags(
            threat.type,
            threat.description,
            threat.tags or ""
        )

        # Step 2: Map to MITRE ATT&CK
        mitre_techniques = map_to_mitre(
            threat.description or "",
            enriched_tags
        )
        mitre_tags = format_mitre_tags(mitre_techniques)

        # Step 3: Merge tags
        all_tags = set(enriched_tags.split(","))
        if mitre_tags:
            all_tags.update(mitre_tags.split(","))
        threat.tags = ",".join(filter(None, all_tags))

        # Step 4: Calculate risk score
        threat.risk_score = calculate_risk_score(threat)

        # Step 5: Generate alert if needed
        alert = generate_alert(threat)
        if alert:
            alert["mitre_techniques"] = mitre_techniques
            alerts.append(alert)

        processed += 1

    db.commit()

    return {
        "processed": processed,
        "alerts_generated": len(alerts),
        "critical": sum(1 for a in alerts if a["alert_level"] == "CRITICAL"),
        "high": sum(1 for a in alerts if a["alert_level"] == "HIGH"),
        "medium": sum(1 for a in alerts if a["alert_level"] == "MEDIUM"),
        "alerts": alerts[:10],
    }