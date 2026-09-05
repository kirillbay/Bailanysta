from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "Bailanysta"
    assert "version" in data


def test_health_v1():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "Bailanysta"
    assert "version" in data
    assert "env" in data


def test_health_root():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_cors_headers():
    r = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    # CORSMiddleware should echo allow-origin when Origin matches
    assert "access-control-allow-origin" in {k.lower(): v for k, v in r.headers.items()}


def test_security_headers():
    r = client.get("/api/v1/health")
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"


def test_404():
    r = client.get("/api/v1/nonexistent")
    assert r.status_code == 404
