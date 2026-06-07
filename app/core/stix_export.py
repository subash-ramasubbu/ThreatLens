import stix2
import json
from datetime import datetime
from app.db.models import ThreatIndicator


def threat_to_stix(threat: ThreatIndicator) -> dict:
    try:
        # Map threat type to STIX pattern
        pattern_map = {
            "ip": f"[ipv4-addr:value = '{threat.value}']",
            "domain": f"[domain-name:value = '{threat.value}']",
            "url": f"[url:value = '{threat.value}']",
            "hash": f"[file:hashes.MD5 = '{threat.value}']",
            "cve": f"[vulnerability:name = '{threat.value}']",
        }

        pattern = pattern_map.get(
            threat.type.lower(),
            f"[indicator:value = '{threat.value}']"
        )

        # Map severity to STIX confidence
        confidence_map = {
            "critical": 90,
            "high": 70,
            "medium": 50,
            "low": 30,
        }
        confidence = confidence_map.get(threat.severity.lower(), 50)

        # Build labels from tags
        labels = []
        if threat.tags:
            labels = [
                tag.strip()
                for tag in threat.tags.split(",")
                if tag.strip()
            ][:5]

        if not labels:
            labels = ["malicious-activity"]

        indicator = stix2.Indicator(
            name=f"{threat.type.upper()}: {threat.value}",
            description=threat.description or f"Threat indicator from {threat.source}",
            pattern=pattern,
            pattern_type="stix",
            valid_from=threat.first_seen or datetime.utcnow(),
            labels=labels,
            confidence=confidence,
            external_references=[
                stix2.ExternalReference(
                    source_name=threat.source,
                    description=f"Risk score: {threat.risk_score}/100",
                )
            ],
        )

        return json.loads(indicator.serialize())

    except Exception as e:
        print(f"Error converting threat {threat.id} to STIX: {e}")
        return None


def export_bundle(threats: list) -> dict:
    stix_objects = []

    # Add identity object
    identity = stix2.Identity(
        name="ThreatLens Platform",
        identity_class="system",
        description="AI-powered threat intelligence platform",
    )
    stix_objects.append(identity)

    # Convert each threat
    for threat in threats:
        stix_obj = threat_to_stix(threat)
        if stix_obj:
            stix_objects.append(stix_obj)

    # Create bundle
    bundle = stix2.Bundle(objects=stix_objects)
    return json.loads(bundle.serialize())