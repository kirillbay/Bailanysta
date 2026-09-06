"""Regression for followers count bug — ensure count increments correctly"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import pytest

@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)

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
def client(db):
    def override():
        yield db
    fastapi_app.dependency_overrides[get_db] = override
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()

def reg(c, u, e):
    return c.post("/api/v1/auth/register", json={"username": u, "email": e, "password": "Secret123!"})

def login(c, ident):
    return c.post("/api/v1/auth/login", json={"identifier": ident, "password": "Secret123!"})

def test_followers_count_increments(client):
    reg(client, "followers_alice", "followers_alice@example.com")
    login(client, "followers_alice@example.com")
    # Check initial count 0
    r = client.get("/api/v1/users/followers_alice")
    assert r.status_code == 200
    assert r.json()["followers_count"] == 0
    # Create bob and follow alice
    client.cookies.clear()
    reg(client, "followers_bob", "followers_bob@example.com")
    login(client, "followers_bob@example.com")
    r = client.post("/api/v1/users/followers_alice/follow")
    assert r.status_code in (200, 201)
    # Check alice followers now 1
    client.cookies.clear()
    login(client, "followers_alice@example.com")
    r = client.get("/api/v1/users/followers_alice")
    assert r.json()["followers_count"] == 1
    # Unfollow
    client.cookies.clear()
    login(client, "followers_bob@example.com")
    r = client.delete("/api/v1/users/followers_alice/follow")
    assert r.status_code == 204
    client.cookies.clear()
    login(client, "followers_alice@example.com")
    r = client.get("/api/v1/users/followers_alice")
    assert r.json()["followers_count"] == 0
