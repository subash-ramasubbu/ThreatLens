def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["platform"] == "ThreatLens"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_threat(client):
    threat_data = {
        "type": "ip",
        "value": "192.168.1.100",
        "severity": "high",
        "confidence": 85.0,
        "source": "test",
        "tags": "test,malicious",
        "description": "Test threat",
        "country": "US",
    }
    response = client.post("/api/threats/", json=threat_data)
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "192.168.1.100"
    assert data["type"] == "ip"


def test_get_threats(client):
    response = client.get("/api/threats/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_threats(client):
    threat_data = {
        "type": "ip",
        "value": "10.0.0.1",
        "severity": "medium",
        "confidence": 50.0,
        "source": "test",
        "tags": "scanning",
        "description": "Scanner IP",
        "country": "CN",
    }
    client.post("/api/threats/", json=threat_data)
    response = client.get("/api/threats/search?q=scanning")
    assert response.status_code == 200


def test_duplicate_threat(client):
    threat_data = {
        "type": "ip",
        "value": "1.2.3.4",
        "severity": "low",
        "confidence": 30.0,
        "source": "test",
        "tags": "",
        "description": "",
        "country": "",
    }
    client.post("/api/threats/", json=threat_data)
    response = client.post("/api/threats/", json=threat_data)
    assert response.status_code == 400


def test_get_threat_by_id(client):
    threat_data = {
        "type": "domain",
        "value": "evil.example.com",
        "severity": "critical",
        "confidence": 95.0,
        "source": "test",
        "tags": "phishing",
        "description": "Phishing domain",
        "country": "RU",
    }
    create_response = client.post("/api/threats/", json=threat_data)
    threat_id = create_response.json()["id"]
    response = client.get(f"/api/threats/{threat_id}")
    assert response.status_code == 200
    assert response.json()["value"] == "evil.example.com"


def test_delete_threat(client):
    threat_data = {
        "type": "hash",
        "value": "abc123def456",
        "severity": "high",
        "confidence": 80.0,
        "source": "test",
        "tags": "malware",
        "description": "Malware hash",
        "country": "",
    }
    create_response = client.post("/api/threats/", json=threat_data)
    threat_id = create_response.json()["id"]
    response = client.delete(f"/api/threats/{threat_id}")
    assert response.status_code == 200