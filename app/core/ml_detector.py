import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
from app.db.models import ThreatIndicator


def extract_features(threat: ThreatIndicator) -> list:
    type_map = {"ip": 1, "domain": 2, "hash": 3, "cve": 4, "url": 5}
    source_map = {"abuseipdb": 1, "alienvault": 2, "nvd": 3, "misp": 4}
    severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}

    tag_count = len(threat.tags.split(",")) if threat.tags else 0
    has_c2 = 1 if threat.tags and "c2" in threat.tags.lower() else 0
    has_ransomware = 1 if threat.tags and "ransomware" in threat.tags.lower() else 0

    return [
        threat.risk_score or 0,
        threat.confidence or 0,
        type_map.get(threat.type.lower(), 0),
        source_map.get(threat.source.lower(), 0),
        severity_map.get(threat.severity.lower(), 2),
        tag_count,
        has_c2,
        has_ransomware,
    ]


def detect_anomalies(threats: list) -> dict:
    if len(threats) < 10:
        return {"error": "Need at least 10 threats for anomaly detection"}

    features = []
    valid_threats = []

    for threat in threats:
        try:
            feat = extract_features(threat)
            features.append(feat)
            valid_threats.append(threat)
        except Exception:
            continue

    if len(features) < 10:
        return {"error": "Not enough valid threats"}

    X = np.array(features)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100,
    )
    predictions = model.fit_predict(X_scaled)
    scores = model.score_samples(X_scaled)

    anomalies = []
    normal = []

    for i, (threat, pred, score) in enumerate(
        zip(valid_threats, predictions, scores)
    ):
        result = {
            "id": threat.id,
            "value": threat.value,
            "type": threat.type,
            "risk_score": threat.risk_score,
            "anomaly_score": round(float(score), 4),
            "is_anomaly": bool(pred == -1),
            "source": threat.source,
            "tags": threat.tags,
        }
        if pred == -1:
            anomalies.append(result)
        else:
            normal.append(result)

    anomalies.sort(key=lambda x: x["anomaly_score"])

    return {
        "total_analyzed": len(valid_threats),
        "anomalies_detected": len(anomalies),
        "normal_count": len(normal),
        "anomaly_rate": round(len(anomalies) / len(valid_threats) * 100, 2),
        "top_anomalies": anomalies[:10],
    }