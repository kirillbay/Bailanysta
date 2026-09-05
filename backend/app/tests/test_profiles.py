"""Profiles + uploads tests — STEP 4."""

import io
import uuid

from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import app.models  # noqa

def _make_image(fmt="PNG", size=(10, 10), color=(255, 0, 0)):
    bio = io.BytesIO()
    im = Image.new("RGB", size, color)
    im.save(bio, format=fmt)
    bio.seek(0)
    return bio

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
    Session = sessionmaker(bind=conn)
    s = Session()
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

def register(client, username="alice", email="alice@example.com", password="Secret123!"):
    return client.post("/api/v1/auth/register", json={"username": username, "email": email, "password": password})

def login(client, identifier, password="Secret123!"):
    return client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})

# Public profile
def test_public_profile_success(client):
    register(client, "pub_user", "pub@example.com")
    r = client.get("/api/v1/users/pub_user")
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "pub_user"
    assert "email" not in data
    assert "password_hash" not in data
    assert "password" not in r.text.lower()
    assert data["id"]

def test_public_profile_404(client):
    r = client.get("/api/v1/users/nonexistent_xyz")
    assert r.status_code == 404

def test_public_no_jwt_leak(client):
    register(client, "leak_test", "leak@example.com")
    r = client.get("/api/v1/users/leak_test")
    assert "jwt" not in r.text.lower()

# Own profile
def test_me_authenticated(client):
    register(client, "me_user", "me@example.com")
    login(client, "me@example.com")
    r = client.get("/api/v1/users/me")
    assert r.status_code == 200
    assert r.json()["username"] == "me_user"
    assert "email" in r.json()

def test_me_unauth(client):
    client.cookies.clear()
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401

# Update
def test_update_own_profile(client):
    register(client, "upd_user", "upd@example.com")
    login(client, "upd@example.com")
    r = client.patch("/api/v1/users/me", json={"display_name": "New Name", "bio": "hello bio"})
    assert r.status_code == 200
    assert r.json()["display_name"] == "New Name"
    assert r.json()["bio"] == "hello bio"
    # persisted
    r2 = client.get("/api/v1/users/me")
    assert r2.json()["display_name"] == "New Name"

def test_update_validation_422(client):
    register(client, "val_user", "val@example.com")
    login(client, "val@example.com")
    # bio too long
    r = client.patch("/api/v1/users/me", json={"bio": "x" * 501})
    assert r.status_code == 422

def test_cannot_patch_other_user(client, db):
    # only /users/me exists, no IDOR endpoint
    register(client, "owner", "owner@example.com")
    login(client, "owner@example.com")
    # try to patch non-existent other endpoint — should 404 or 405
    r = client.patch("/api/v1/users/other_user", json={"bio": "hack"})
    assert r.status_code in (404, 405, 422)

def test_update_unauth(client):
    client.cookies.clear()
    r = client.patch("/api/v1/users/me", json={"bio": "hack"})
    assert r.status_code == 401

# Upload
def test_upload_avatar_success(client):
    register(client, "av_user", "av@example.com")
    login(client, "av@example.com")
    img = _make_image("PNG")
    r = client.post("/api/v1/users/me/avatar", files={"file": ("avatar.png", img, "image/png")})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["avatar_url"] is not None
    assert data["avatar_url"].startswith("/uploads/avatars/")
    # url should be safe, not containing original filename
    assert "avatar.png" not in data["avatar_url"]
    # static serve check
    url = data["avatar_url"]
    r2 = client.get(url)
    assert r2.status_code == 200
    assert r2.headers["content-type"].startswith("image/")

def test_upload_cover_success(client):
    register(client, "cover_user", "cover@example.com")
    login(client, "cover@example.com")
    img = _make_image("JPEG")
    r = client.post("/api/v1/users/me/cover", files={"file": ("cover.jpg", img, "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["cover_url"].startswith("/uploads/covers/")

def test_upload_unauth(client):
    client.cookies.clear()
    img = _make_image("PNG")
    r = client.post("/api/v1/users/me/avatar", files={"file": ("a.png", img, "image/png")})
    assert r.status_code == 401

def test_upload_unsupported_mime(client):
    register(client, "mime_user", "mime@example.com")
    login(client, "mime@example.com")
    r = client.post("/api/v1/users/me/avatar", files={"file": ("evil.exe", b"not an image", "application/octet-stream")})
    assert r.status_code == 415

def test_upload_oversized(client):
    register(client, "big_user", "big@example.com")
    login(client, "big@example.com")
    # create 6 MB payload (>5 MB limit)
    big = b"\xff" * (6 * 1024 * 1024)
    r = client.post("/api/v1/users/me/avatar", files={"file": ("big.png", big, "image/png")})
    assert r.status_code in (413, 415)

def test_upload_malicious_filename(client):
    register(client, "evil_user", "evil@example.com")
    login(client, "evil@example.com")
    img = _make_image("PNG")
    r = client.post("/api/v1/users/me/avatar", files={"file": ("../../etc/passwd", img, "image/png")})
    assert r.status_code == 200
    url = r.json()["avatar_url"]
    assert ".." not in url
    assert "passwd" not in url
    assert url.startswith("/uploads/avatars/")

def test_upload_generated_safe_filename(client):
    register(client, "safe_user", "safe@example.com")
    login(client, "safe@example.com")
    img1 = _make_image("PNG")
    img2 = _make_image("PNG")
    r1 = client.post("/api/v1/users/me/avatar", files={"file": ("a.png", img1, "image/png")})
    r2 = client.post("/api/v1/users/me/avatar", files={"file": ("a.png", img2, "image/png")})
    assert r1.json()["avatar_url"] != r2.json()["avatar_url"]

def test_upload_no_path_traversal(client):
    register(client, "trav_user", "trav@example.com")
    login(client, "trav@example.com")
    img = _make_image("PNG")
    r = client.post("/api/v1/users/me/avatar", files={"file": ("avatar.png", img, "image/png")})
    url = r.json()["avatar_url"]
    # ensure not outside uploads
    assert not url.startswith("/etc")
    assert "/uploads/" in url

def test_public_profile_no_email_leak_after_update(client):
    register(client, "priv_user", "priv@example.com")
    login(client, "priv@example.com")
    client.patch("/api/v1/users/me", json={"bio": "new bio"})
    # public view should still not leak email
    client.cookies.clear()
    r = client.get("/api/v1/users/priv_user")
    assert "priv@example.com" not in r.text
    assert "password" not in r.text.lower()
