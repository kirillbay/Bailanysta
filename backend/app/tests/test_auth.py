"""Comprehensive auth tests per STEP 3 §17."""

import uuid
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token, COOKIE_NAME
from app.main import app
from app.models.user import User

# Use SQLite test DB via conftest fixtures — override get_db
from app.database.session import get_db
from app.database.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    conn = test_engine.connect()
    trans = conn.begin()
    Session = sessionmaker(bind=conn)
    session = Session()
    yield session
    session.close()
    trans.rollback()
    conn.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Helpers
def register(client, username="alice", email="alice@example.com", password="Secret123!", display_name=None):
    body = {"username": username, "email": email, "password": password}
    if display_name:
        body["display_name"] = display_name
    return client.post("/api/v1/auth/register", json=body)


def login(client, identifier, password):
    return client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})


# ── Registration ──

def test_register_success(client, db_session):
    r = register(client, username="reg_ok", email="reg_ok@example.com", password="Secret123!")
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["username"] == "reg_ok"
    assert data["email"] == "reg_ok@example.com"
    assert "password" not in r.text.lower()
    assert "password_hash" not in r.text
    assert "Set-Cookie" in r.headers
    assert COOKIE_NAME in r.headers["Set-Cookie"]
    assert "httponly" in r.headers["Set-Cookie"].lower()
    # password stored as hash
    user = db_session.query(User).filter_by(username="reg_ok").first()
    assert user is not None
    assert user.password_hash != "Secret123!"
    assert user.password_hash is not None


def test_register_duplicate_username(client):
    register(client, username="dupuser", email="dup1@example.com", password="Secret123!")
    r = register(client, username="dupuser", email="dup2@example.com", password="Secret123!")
    assert r.status_code == 409


def test_register_duplicate_email(client):
    register(client, username="uniq1", email="dup@example.com", password="Secret123!")
    r = register(client, username="uniq2", email="dup@example.com", password="Secret123!")
    assert r.status_code == 409


def test_register_duplicate_email_case_variant(client):
    register(client, username="case1", email="Case@Example.com", password="Secret123!")
    r = register(client, username="case2", email="case@example.com", password="Secret123!")
    # Should be 409 because we lower-case emails
    assert r.status_code == 409


def test_register_invalid_email(client):
    r = register(client, username="badmail", email="not-an-email", password="Secret123!")
    assert r.status_code == 422


def test_register_invalid_password(client):
    r = register(client, username="shortpass", email="short@example.com", password="short")
    assert r.status_code == 422


def test_register_invalid_username(client):
    r = register(client, username="ab", email="ab@example.com", password="Secret123!")
    assert r.status_code == 422
    r2 = register(client, username="bad name", email="bad2@example.com", password="Secret123!")
    assert r2.status_code == 422


def test_register_password_not_returned(client):
    r = register(client, username="no_leak", email="noleak@example.com", password="Secret123!")
    assert r.status_code == 201
    assert "password_hash" not in r.text
    assert "Secret123!" not in r.text


# ── Login ──

def test_login_success_by_email(client):
    register(client, username="login_email", email="login_email@example.com", password="Secret123!")
    r = login(client, "login_email@example.com", "Secret123!")
    assert r.status_code == 200
    assert r.json()["username"] == "login_email"
    assert COOKIE_NAME in r.headers.get("Set-Cookie", "")


def test_login_success_by_username(client):
    register(client, username="login_user", email="login_user@example.com", password="Secret123!")
    r = login(client, "login_user", "Secret123!")
    assert r.status_code == 200


def test_login_success_email_case_insensitive(client):
    register(client, username="ci_user", email="ci@example.com", password="Secret123!")
    r = login(client, "CI@EXAMPLE.COM", "Secret123!")
    assert r.status_code == 200


def test_login_wrong_password(client):
    register(client, username="wp_user", email="wp@example.com", password="Secret123!")
    r = login(client, "wp@example.com", "Wrongpass123!")
    assert r.status_code == 401
    assert "Invalid credentials" in r.text


def test_login_unknown_user(client):
    r = login(client, "nonexistent@example.com", "whatever123")
    assert r.status_code == 401
    r2 = login(client, "no_such_user", "whatever123")
    assert r2.status_code == 401


def test_login_inactive_user(client, db_session):
    register(client, username="inactive", email="inactive@example.com", password="Secret123!")
    user = db_session.query(User).filter_by(username="inactive").first()
    user.is_active = False
    db_session.commit()
    r = login(client, "inactive@example.com", "Secret123!")
    assert r.status_code == 401
    # reactivate for other tests isolation (new db per module but still)
    user.is_active = True
    db_session.commit()


def test_login_cookie_attributes(client):
    register(client, username="cookie_user", email="cookie@example.com", password="Secret123!")
    r = login(client, "cookie@example.com", "Secret123!")
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie or "httponly" in cookie.lower()
    assert "SameSite" in cookie or "samesite" in cookie.lower()
    assert "Path=/" in cookie


# ── /auth/me ──

def test_me_authenticated(client):
    register(client, username="me_user", email="me@example.com", password="Secret123!")
    login(client, "me@example.com", "Secret123!")
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "me_user"
    assert "password_hash" not in r.text


def test_me_no_cookie(client):
    # fresh client without auth
    from fastapi.testclient import TestClient

    # create new client without cookies
    with TestClient(app) as fresh:
        # override db still needed
        from app.database.session import get_db as _get_db

        # reuse same engine? easier to just test unauthenticated without DB override
        # but unauthenticated should 401 regardless of DB
        r = fresh.get("/api/v1/auth/me")
        assert r.status_code == 401


def test_me_invalid_token(client):
    client.cookies.set(COOKIE_NAME, "invalid.token.here")
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_expired_token(client, db_session):
    # create user directly
    from app.core.security import hash_password

    user = User(username="exp_user", email="exp@example.com", password_hash=hash_password("Secret123!"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    expired = create_access_token(user.id, expires_minutes=-1)
    client.cookies.set(COOKIE_NAME, expired)
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
    assert "expired" in r.text.lower() or "invalid" in r.text.lower()


def test_me_modified_token(client):
    register(client, username="mod_user", email="mod@example.com", password="Secret123!")
    r = login(client, "mod@example.com", "Secret123!")
    token = r.cookies.get(COOKIE_NAME) or client.cookies.get(COOKIE_NAME)
    assert token is not None
    # tamper by appending garbage — must invalidate signature
    tampered = token + "x"
    client.cookies.set(COOKIE_NAME, tampered)
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_nonexistent_user(client):
    fake_id = uuid.uuid4()
    token = create_access_token(fake_id)
    client.cookies.set(COOKIE_NAME, token)
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


# ── Logout ──

def test_logout_clears_cookie(client):
    register(client, username="logout_user", email="logout@example.com", password="Secret123!")
    login(client, "logout@example.com", "Secret123!")
    assert client.get("/api/v1/auth/me").status_code == 200
    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 204
    # after logout, me should 401 (cookie cleared)
    # TestClient keeps cookies but logout deletes; check Set-Cookie header
    assert "Set-Cookie" in r.headers
    # subsequent me without valid cookie
    client.cookies.clear()
    assert client.get("/api/v1/auth/me").status_code == 401


def test_logout_without_auth_fails(client):
    client.cookies.clear()
    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 401


# ── Security ──

def test_password_never_in_response(client):
    r = register(client, username="sec_user", email="sec@example.com", password="Secret123!")
    assert "Secret123!" not in r.text
    assert "password" not in r.json()  # no password key
    r2 = login(client, "sec@example.com", "Secret123!")
    assert "Secret123!" not in r2.text
    assert "password" not in r2.json()


def test_jwt_signature_tampered_rejected(client):
    register(client, username="sig_user", email="sig@example.com", password="Secret123!")
    r = login(client, "sig@example.com", "Secret123!")
    token = client.cookies.get(COOKIE_NAME)
    # Create token with different secret should fail
    fake_token = jwt.encode(
        {"sub": str(uuid.uuid4()), "exp": 9999999999, "iat": 1000000000, "type": "access"},
        "wrong-secret-key",
        algorithm="HS256",
    )
    client.cookies.set(COOKIE_NAME, fake_token)
    assert client.get("/api/v1/auth/me").status_code == 401
    # Also alg none attempt
    none_header = jwt.encode(
        {"sub": str(uuid.uuid4()), "exp": 9999999999, "iat": 1000000000, "type": "access"},
        key="",
        algorithm="HS256",
    )
    # try none alg token (PyJWT won't allow none without key, but we test empty)
    client.cookies.set(COOKIE_NAME, "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjMifQ.")
    assert client.get("/api/v1/auth/me").status_code == 401
