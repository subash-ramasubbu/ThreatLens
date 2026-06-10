def test_export_summary(client):
    response = client.get("/api/export/summary")
    assert response.status_code in [200, 404]


def test_cache_stats(client):
    response = client.get("/api/cache/stats")
    assert response.status_code == 200


def test_correlate_empty(client):
    response = client.post("/api/correlate/run")
    assert response.status_code == 200
    data = response.json()
    assert "processed" in data


def test_alerts_critical(client):
    response = client.get("/api/alerts/critical")
    assert response.status_code == 200
    assert "total" in response.json()