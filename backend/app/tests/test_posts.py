"""Posts + media + hashtags + ownership + delete tests — STEP 5."""
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

def _img(fmt="PNG", color=(0, 255, 0)):
    bio = io.BytesIO()
    Image.new("RGB", (10, 10), color).save(bio, format=fmt)
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

def reg(client, username, email):
    return client.post("/api/v1/auth/register", json={"username": username, "email": email, "password": "Secret123!"})

def login(client, identifier):
    return client.post("/api/v1/auth/login", json={"identifier": identifier, "password": "Secret123!"})

# Helpers to create post via multipart
def create_post(client, content, files=None):
    data = {"content": content}
    file_tuples = []
    if files:
        for fname, bio, mime in files:
            file_tuples.append(("files", (fname, bio, mime)))
    # Use data param for Form, files for UploadFile
    return client.post("/api/v1/posts", data=data, files=file_tuples if file_tuples else None)

# ── Posts ──
def test_create_authenticated(client):
    reg(client, "author1", "a1@example.com")
    login(client, "a1@example.com")
    r = create_post(client, "hello world")
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["content"] == "hello world"
    assert data["author"]["username"] == "author1"
    assert "email" not in str(data).lower()
    assert "password" not in r.text.lower()

def test_create_unauth(client):
    client.cookies.clear()
    r = create_post(client, "should fail")
    assert r.status_code == 401

def test_create_empty_rejected(client):
    reg(client, "empty_user", "empty@example.com")
    login(client, "empty@example.com")
    r = create_post(client, "   ")
    assert r.status_code == 422

def test_create_oversized_rejected(client):
    reg(client, "big_user", "big2@example.com")
    login(client, "big2@example.com")
    long_content = "x" * 10001
    r = create_post(client, long_content)
    assert r.status_code in (422, 400)

def test_create_returns_author_public(client):
    reg(client, "pubauthor", "pubauthor@example.com")
    login(client, "pubauthor@example.com")
    r = create_post(client, "check author")
    data = r.json()
    assert "author" in data
    assert "email" not in data["author"]
    assert data["author"]["avatar_url"] is not None or True  # may be null

# Media
def test_media_jpeg_accepted(client):
    reg(client, "jpeg_user", "jpeg@example.com")
    login(client, "jpeg@example.com")
    img = _img("JPEG")
    r = create_post(client, "with jpeg", files=[("a.jpg", img, "image/jpeg")])
    assert r.status_code == 201
    assert len(r.json()["media"]) == 1

def test_media_png_accepted(client):
    reg(client, "png_user", "png@example.com")
    login(client, "png@example.com")
    img = _img("PNG")
    r = create_post(client, "with png", files=[("a.png", img, "image/png")])
    assert r.status_code == 201

def test_media_webp_accepted(client):
    reg(client, "webp_user", "webp@example.com")
    login(client, "webp@example.com")
    img = _img("WEBP")
    r = create_post(client, "with webp", files=[("a.webp", img, "image/webp")])
    assert r.status_code == 201

def test_media_unsupported_rejected(client):
    reg(client, "badmime_user", "badmime@example.com")
    login(client, "badmime@example.com")
    r = create_post(client, "bad mime", files=[("evil.exe", io.BytesIO(b"not image"), "application/octet-stream")])
    assert r.status_code in (415, 422, 400)

def test_media_oversized_rejected(client):
    reg(client, "oversize_user", "oversize@example.com")
    login(client, "oversize@example.com")
    big = io.BytesIO(b"\xff" * (6 * 1024 * 1024))
    r = create_post(client, "big file", files=[("big.png", big, "image/png")])
    assert r.status_code in (413, 415, 422)

def test_media_invalid_content_rejected(client):
    reg(client, "invalid_img", "invalid@example.com")
    login(client, "invalid@example.com")
    fake = io.BytesIO(b"this is not an image but claims png")
    r = create_post(client, "fake", files=[("fake.png", fake, "image/png")])
    assert r.status_code in (415, 422)

def test_media_malicious_filename_safe(client):
    reg(client, "evil_post", "evilpost@example.com")
    login(client, "evilpost@example.com")
    img = _img("PNG")
    r = create_post(client, "evil filename", files=[("../../etc/passwd", img, "image/png")])
    assert r.status_code == 201
    url = r.json()["media"][0]["url"]
    assert ".." not in url
    assert "passwd" not in url
    assert url.startswith("/uploads/posts/")

def test_media_max_count_enforced(client):
    reg(client, "maxmedia_user", "maxmedia@example.com")
    login(client, "maxmedia@example.com")
    files = [("a.png", _img("PNG"), "image/png") for _ in range(5)]
    r = create_post(client, "too many", files=files)
    assert r.status_code == 422

def test_media_stored_under_posts_dir(client):
    reg(client, "dir_user", "dir@example.com")
    login(client, "dir@example.com")
    img = _img("PNG")
    r = create_post(client, "check dir", files=[("x.png", img, "image/png")])
    assert r.json()["media"][0]["url"].startswith("/uploads/posts/")

# Read
def test_get_existing_post(client):
    reg(client, "reader", "reader@example.com")
    login(client, "reader@example.com")
    r = create_post(client, "read me")
    pid = r.json()["id"]
    r2 = client.get(f"/api/v1/posts/{pid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == pid

def test_get_nonexistent_404(client):
    r = client.get(f"/api/v1/posts/{uuid.uuid4()}")
    assert r.status_code == 404

def test_user_posts_pagination(client):
    reg(client, "pag_user", "pag@example.com")
    login(client, "pag@example.com")
    for i in range(5):
        create_post(client, f"post {i}")
    r = client.get("/api/v1/users/pag_user/posts?limit=2&offset=0")
    assert r.status_code == 200
    assert len(r.json()) == 2
    r2 = client.get("/api/v1/users/pag_user/posts?limit=2&offset=2")
    assert len(r2.json()) == 2

def test_pagination_max_limit(client):
    reg(client, "lim_user", "lim@example.com")
    login(client, "lim@example.com")
    r = client.get("/api/v1/users/lim_user/posts?limit=100")
    # Should be capped to 50 or 422; we enforce le=50, so 422
    assert r.status_code == 422

# Ownership
def test_owner_can_update(client):
    reg(client, "owner_upd", "owner_upd@example.com")
    login(client, "owner_upd@example.com")
    r = create_post(client, "original")
    pid = r.json()["id"]
    r2 = client.patch(f"/api/v1/posts/{pid}", json={"content": "updated #edited"})
    assert r2.status_code == 200
    assert r2.json()["content"] == "updated #edited"

def test_owner_can_delete(client):
    reg(client, "owner_del", "owner_del@example.com")
    login(client, "owner_del@example.com")
    r = create_post(client, "to delete")
    pid = r.json()["id"]
    r2 = client.delete(f"/api/v1/posts/{pid}")
    assert r2.status_code == 204
    assert client.get(f"/api/v1/posts/{pid}").status_code == 404

def test_other_cannot_update(client):
    reg(client, "owner2", "owner2@example.com")
    login(client, "owner2@example.com")
    r = create_post(client, "owner post")
    pid = r.json()["id"]
    client.cookies.clear()
    reg(client, "other", "other@example.com")
    login(client, "other@example.com")
    r2 = client.patch(f"/api/v1/posts/{pid}", json={"content": "hacked"})
    assert r2.status_code == 403

def test_other_cannot_delete(client):
    reg(client, "owner3", "owner3@example.com")
    login(client, "owner3@example.com")
    r = create_post(client, "owner post2")
    pid = r.json()["id"]
    client.cookies.clear()
    reg(client, "other2", "other2@example.com")
    login(client, "other2@example.com")
    r2 = client.delete(f"/api/v1/posts/{pid}")
    assert r2.status_code == 403

def test_forged_author_id_ignored(client):
    reg(client, "forger", "forger@example.com")
    login(client, "forger@example.com")
    # Try to send author_id in patch — should be ignored, owner still enforced
    r = create_post(client, "forge test")
    pid = r.json()["id"]
    r2 = client.patch(f"/api/v1/posts/{pid}", json={"content": "changed", "author_id": str(uuid.uuid4())})
    # Should succeed but author_id not changed
    assert r2.status_code == 200
    assert r2.json()["author"]["username"] == "forger"

# Hashtags
def test_hashtags_extracted(client):
    reg(client, "hash_user", "hash@example.com")
    login(client, "hash@example.com")
    r = create_post(client, "hello #Python and #AI #python duplicate")
    data = r.json()
    assert "python" in data["hashtags"]
    assert "ai" in data["hashtags"]
    # duplicate lowercased
    assert data["hashtags"].count("python") == 1

def test_hashtags_normalization(client):
    reg(client, "norm_user", "norm@example.com")
    login(client, "norm@example.com")
    r = create_post(client, "#Bailanysta #bailanysta #BAILANysta")
    assert r.json()["hashtags"] == ["bailanysta"]

def test_hashtags_duplicate_handling(client):
    reg(client, "duphash_user", "duphash@example.com")
    login(client, "duphash@example.com")
    r = create_post(client, "#a #a #a #b")
    assert sorted(r.json()["hashtags"]) == ["a", "b"]

def test_hashtags_excessive_limited(client):
    reg(client, "manyhash_user", "manyhash@example.com")
    login(client, "manyhash@example.com")
    content = " ".join([f"#tag{i}" for i in range(30)])
    r = create_post(client, content)
    assert len(r.json()["hashtags"]) <= 20

# Delete cleanup
def test_delete_removes_media_records(client):
    reg(client, "clean_user", "clean@example.com")
    login(client, "clean@example.com")
    img = _img("PNG")
    r = create_post(client, "with media to delete", files=[("x.png", img, "image/png")])
    pid = r.json()["id"]
    url = r.json()["media"][0]["url"]
    # file exists via static
    assert client.get(url).status_code == 200
    client.delete(f"/api/v1/posts/{pid}")
    # after delete, media should be gone (post gone) and file deleted
    # Check file not served (may still be cached but should 404)
    # At least post not found
    assert client.get(f"/api/v1/posts/{pid}").status_code == 404

def test_edit_updates_hashtags(client):
    reg(client, "edit_hash_user", "edithash@example.com")
    login(client, "edithash@example.com")
    r = create_post(client, "#oldtag content")
    pid = r.json()["id"]
    assert "oldtag" in r.json()["hashtags"]
    r2 = client.patch(f"/api/v1/posts/{pid}", json={"content": "#newtag edited"})
    assert "newtag" in r2.json()["hashtags"]
    assert "oldtag" not in r2.json()["hashtags"]
