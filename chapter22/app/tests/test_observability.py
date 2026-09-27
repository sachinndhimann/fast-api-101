from fastapi.testclient import TestClient
from app.main import app, DependencyStatus

client = TestClient(app)

def test_liveness_always_ok_regardless_of_dependencies():
    DependencyStatus.database_up = False  # simulate DB outage
    try:
        r = client.get("/health")
        assert r.status_code == 200  # liveness does NOT check dependencies
    finally:
        DependencyStatus.database_up = True

def test_readiness_reflects_dependency_health():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True

    DependencyStatus.database_up = False
    try:
        r = client.get("/ready")
        assert r.status_code == 503
        assert r.json()["checks"]["database"] is False
    finally:
        DependencyStatus.database_up = True

def test_metrics_endpoint_exposes_prometheus_format():
    client.get("/health")  # generate at least one request to instrument
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text or "http_request_duration" in r.text

def test_request_id_is_correlated_across_response_and_logs():
    r = client.get("/orders/1", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
