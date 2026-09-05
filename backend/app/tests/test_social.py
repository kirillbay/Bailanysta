"""Feed + likes/comments/reposts/bookmarks tests — STEP 6."""
import uuid, io
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import app.models  # noqa
import pytest

def _img():
    bio = io.BytesIO()
    Image.new("RGB", (10,10), (0,255,0)).save(bio, format="PNG")
    bio.seek(0)
    return bio

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

def reg(client, u, e):
    return client.post("/api/v1/auth/register", json={"username": u, "email": e, "password": "Secret123!"})

def login(client, ident):
    return client.post("/api/v1/auth/login", json={"identifier": ident, "password": "Secret123!"})

def make_post(client, content="hello", files=None):
    data = {"content": content}
    files_t = []
    if files:
        for fname, bio, mime in files:
            files_t.append(("files", (fname, bio, mime)))
    return client.post("/api/v1/posts", data=data, files=files_t if files_t else None)

# Feed
def test_feed_authenticated(client):
    reg(client, "feed_user", "feed@example.com")
    login(client, "feed@example.com")
    make_post(client, "feed post 1")
    make_post(client, "feed post 2")
    r = client.get("/api/v1/feed?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2
    # ordering desc
    assert data[0]["created_at"] >= data[1]["created_at"]
    assert "likes_count" in data[0]
    assert "liked_by_me" in data[0]

def test_feed_pagination(client):
    reg(client, "pag_feed", "pagfeed@example.com")
    login(client, "pagfeed@example.com")
    for i in range(5):
        make_post(client, f"pag {i}")
    r = client.get("/api/v1/feed?limit=2&offset=0")
    assert len(r.json()) == 2
    r2 = client.get("/api/v1/feed?limit=2&offset=2")
    assert len(r2.json()) == 2

def test_feed_empty(client):
    reg(client, "empty_feed_user", "emptyfeed@example.com")
    login(client, "emptyfeed@example.com")
    # New isolated DB per module? But feed contains previous posts, so empty not guaranteed. Test that feed returns list
    r = client.get("/api/v1/feed?limit=5&offset=1000")
    assert r.status_code == 200
    assert r.json() == []

def test_feed_requires_auth(client):
    client.cookies.clear()
    r = client.get("/api/v1/feed")
    assert r.status_code == 401

# Likes
def test_like_and_unlike(client):
    reg(client, "like_user", "like@example.com")
    login(client, "like@example.com")
    pid = make_post(client, "like test").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/like")
    assert r.status_code == 201
    # check liked_by_me
    r2 = client.get(f"/api/v1/posts/{pid}")
    assert r2.json()["liked_by_me"] is True
    assert r2.json()["likes_count"] == 1
    # unlike
    r3 = client.delete(f"/api/v1/posts/{pid}/like")
    assert r3.status_code == 204
    r4 = client.get(f"/api/v1/posts/{pid}")
    assert r4.json()["liked_by_me"] is False
    assert r4.json()["likes_count"] == 0

def test_duplicate_like_idempotent(client):
    reg(client, "dup_like", "duplike@example.com")
    login(client, "duplike@example.com")
    pid = make_post(client, "dup like").json()["id"]
    client.post(f"/api/v1/posts/{pid}/like")
    r = client.post(f"/api/v1/posts/{pid}/like")
    assert r.status_code in (200, 201)  # Already liked returns 201 with detail
    r2 = client.get(f"/api/v1/posts/{pid}")
    assert r2.json()["likes_count"] == 1

def test_like_unauth(client):
    # need a post first
    reg(client, "like_owner", "likeowner@example.com")
    login(client, "likeowner@example.com")
    pid = make_post(client, "like owner post").json()["id"]
    client.cookies.clear()
    r = client.post(f"/api/v1/posts/{pid}/like")
    assert r.status_code == 401

def test_like_nonexistent(client):
    reg(client, "like_nonex", "likenonex@example.com")
    login(client, "likenonex@example.com")
    r = client.post(f"/api/v1/posts/{uuid.uuid4()}/like")
    assert r.status_code == 404

def test_like_isolation(client):
    reg(client, "userA", "a@example.com")
    login(client, "a@example.com")
    pid = make_post(client, "isolation").json()["id"]
    client.cookies.clear()
    reg(client, "userB", "b@example.com")
    login(client, "b@example.com")
    r = client.get(f"/api/v1/posts/{pid}")
    assert r.json()["liked_by_me"] is False
    client.post(f"/api/v1/posts/{pid}/like")
    r2 = client.get(f"/api/v1/posts/{pid}")
    assert r2.json()["liked_by_me"] is True
    # A should still not liked
    client.cookies.clear()
    login(client, "a@example.com")
    r3 = client.get(f"/api/v1/posts/{pid}")
    assert r3.json()["liked_by_me"] is False

# Comments
def test_comment_create_and_read(client):
    reg(client, "comm_user", "comm@example.com")
    login(client, "comm@example.com")
    pid = make_post(client, "comment post").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "nice!"})
    assert r.status_code == 201
    assert r.json()["content"] == "nice!"
    r2 = client.get(f"/api/v1/posts/{pid}/comments")
    assert len(r2.json()) == 1

def test_comment_update_own(client):
    reg(client, "comm_upd", "commupd@example.com")
    login(client, "commupd@example.com")
    pid = make_post(client, "upd comment post").json()["id"]
    cid = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "orig"}).json()["id"]
    r = client.patch(f"/api/v1/comments/{cid}", json={"content": "edited"})
    assert r.status_code == 200
    assert r.json()["content"] == "edited"

def test_comment_delete_own(client):
    reg(client, "comm_del", "commdel@example.com")
    login(client, "commdel@example.com")
    pid = make_post(client, "del comment").json()["id"]
    cid = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "to delete"}).json()["id"]
    r = client.delete(f"/api/v1/comments/{cid}")
    assert r.status_code == 204
    assert len(client.get(f"/api/v1/posts/{pid}/comments").json()) == 0

def test_comment_cannot_update_other(client):
    reg(client, "owner_c", "ownerc@example.com")
    login(client, "ownerc@example.com")
    pid = make_post(client, "owner comment").json()["id"]
    cid = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "owner"}).json()["id"]
    client.cookies.clear()
    reg(client, "hacker_c", "hackerc@example.com")
    login(client, "hackerc@example.com")
    r = client.patch(f"/api/v1/comments/{cid}", json={"content": "hacked"})
    assert r.status_code == 403
    r2 = client.delete(f"/api/v1/comments/{cid}")
    assert r2.status_code == 403

def test_comment_empty_rejected(client):
    reg(client, "empty_comm", "emptycomm@example.com")
    login(client, "emptycomm@example.com")
    pid = make_post(client, "empty comm post").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "   "})
    assert r.status_code == 422

def test_comment_too_long(client):
    reg(client, "long_comm", "longcomm@example.com")
    login(client, "longcomm@example.com")
    pid = make_post(client, "long").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "x"*2001})
    assert r.status_code == 422

def test_comment_unauth(client):
    reg(client, "comm_owner2", "commowner2@example.com")
    login(client, "comm_owner2@example.com")
    pid = make_post(client, "comm owner2").json()["id"]
    client.cookies.clear()
    r = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "hack"})
    assert r.status_code == 401

def test_comment_nonexistent_post(client):
    reg(client, "comm_nonex", "commnonex@example.com")
    login(client, "commnonex@example.com")
    r = client.post(f"/api/v1/posts/{uuid.uuid4()}/comments", json={"content": "hi"})
    assert r.status_code == 404

# Reposts
def test_repost_and_unrepost(client):
    reg(client, "repost_user", "repost@example.com")
    login(client, "repost@example.com")
    pid = make_post(client, "repost test").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/repost")
    assert r.status_code == 201
    assert client.get(f"/api/v1/posts/{pid}").json()["reposted_by_me"] is True
    assert client.get(f"/api/v1/posts/{pid}").json()["reposts_count"] == 1
    client.delete(f"/api/v1/posts/{pid}/repost")
    assert client.get(f"/api/v1/posts/{pid}").json()["reposted_by_me"] is False

def test_duplicate_repost(client):
    reg(client, "dup_repost", "duprepost@example.com")
    login(client, "duprepost@example.com")
    pid = make_post(client, "dup repost").json()["id"]
    client.post(f"/api/v1/posts/{pid}/repost")
    r = client.post(f"/api/v1/posts/{pid}/repost")
    assert r.status_code in (200,201)
    assert client.get(f"/api/v1/posts/{pid}").json()["reposts_count"] == 1

def test_repost_unauth(client):
    reg(client, "repost_owner", "repostowner@example.com")
    login(client, "repostowner@example.com")
    pid = make_post(client, "repost owner").json()["id"]
    client.cookies.clear()
    assert client.post(f"/api/v1/posts/{pid}/repost").status_code == 401

# Bookmarks
def test_bookmark_and_remove(client):
    reg(client, "bm_user", "bm@example.com")
    login(client, "bm@example.com")
    pid = make_post(client, "bm test").json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/bookmark")
    assert r.status_code == 201
    assert client.get(f"/api/v1/posts/{pid}").json()["bookmarked_by_me"] is True
    r2 = client.get("/api/v1/bookmarks")
    assert any(p["id"] == pid for p in r2.json())
    client.delete(f"/api/v1/posts/{pid}/bookmark")
    assert client.get(f"/api/v1/posts/{pid}").json()["bookmarked_by_me"] is False

def test_duplicate_bookmark(client):
    reg(client, "dup_bm", "dupbm@example.com")
    login(client, "dupbm@example.com")
    pid = make_post(client, "dup bm").json()["id"]
    client.post(f"/api/v1/posts/{pid}/bookmark")
    r = client.post(f"/api/v1/posts/{pid}/bookmark")
    assert r.status_code in (200,201)

def test_bookmarks_isolation(client):
    reg(client, "bm_owner", "bmowner@example.com")
    login(client, "bmowner@example.com")
    pid = make_post(client, "bm owner post").json()["id"]
    client.post(f"/api/v1/posts/{pid}/bookmark")
    client.cookies.clear()
    reg(client, "bm_other", "bmother@example.com")
    login(client, "bmother@example.com")
    r = client.get("/api/v1/bookmarks")
    assert not any(p["id"] == pid for p in r.json())

def test_bookmark_unauth(client):
    client.cookies.clear()
    assert client.get("/api/v1/bookmarks").status_code == 401
    assert client.post(f"/api/v1/posts/{uuid.uuid4()}/bookmark").status_code == 401
