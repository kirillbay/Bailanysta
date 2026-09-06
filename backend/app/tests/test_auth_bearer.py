"""Test Bearer token fallback for cross-site"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import app.models

@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def db(engine):
    conn = engine.connect()
    trans = conn.begin()
    S = sessionmaker(bind=conn)
    s = S()
    yield s
    s.close()
    trans.rollback()
    conn.close()

@pytest.fixture()
def client(db, engine):
    def override():
        S = sessionmaker(bind=engine)
        s = S()
        try:
            yield s
        finally:
            s.close()
    fastapi_app.dependency_overrides[get_db] = override
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()

def test_register_returns_token(client):
    r = client.post("/api/v1/auth/register", json={"username": "bearer_test", "email": "bearer@test.com", "password": "Secret123!"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "bearer_test"

def test_bearer_auth_without_cookie(client):
    # Register first
    r = client.post("/api/v1/auth/register", json={"username": "bearer_test2", "email": "bearer2@test.com", "password": "Secret123!"})
    # For this test, we need a fresh client without cookie but with Bearer
    # Get token from register
    token = r.json()["access_token"]
    # Clear cookies and use Bearer
    client.cookies.clear()
    r2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200, f"Expected 200 with Bearer, got {r2.status_code} {r2.text}"
    assert r2.json()["username"] == "bearer_test2"

def test_cookie_still_works(client):
    r = client.post("/api/v1/auth/register", json={"username": "bearer_test3", "email": "bearer3@test.com", "password": "Secret123!"})
    assert r.status_code == 201
    # Subsequent request with cookie should work (TestClient handles cookie automatically)
    r2 = client.get("/api/v1/auth/me")
    assert r2.status_code == 200

def test_demo_returns_token(client):
    r = client.post("/api/v1/auth/demo")
    assert r.status_code == 200
    assert "access_token" in r.json()
