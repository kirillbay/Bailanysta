"""Follow + Search + Hashtags tests — STEP 7."""
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

def make_post(client, content):
    return client.post("/api/v1/posts", data={"content": content})

# Follow
def test_follow_unfollow(client):
    reg(client, "follower", "follower@example.com")
    reg(client, "followed", "followed@example.com")
    login(client, "follower@example.com")
    r = client.post("/api/v1/users/followed/follow")
    assert r.status_code == 201
    # check counts
    r2 = client.get("/api/v1/users/followed")
    assert r2.json()["followers_count"] == 1
    assert r2.json()["is_following"] is True
    r3 = client.delete("/api/v1/users/followed/follow")
    assert r3.status_code == 204
    r4 = client.get("/api/v1/users/followed")
    assert r4.json()["followers_count"] == 0
    assert r4.json()["is_following"] is False

def test_duplicate_follow(client):
    reg(client, "dup_follower", "dupfollower@example.com")
    reg(client, "dup_followed", "dupfollowed@example.com")
    login(client, "dupfollower@example.com")
    client.post("/api/v1/users/dup_followed/follow")
    r = client.post("/api/v1/users/dup_followed/follow")
    assert r.status_code in (200,201)
    # still 1
    assert client.get("/api/v1/users/dup_followed").json()["followers_count"] == 1

def test_self_follow_rejected(client):
    reg(client, "self_user", "self@example.com")
    login(client, "self@example.com")
    r = client.post("/api/v1/users/self_user/follow")
    assert r.status_code == 400

def test_follow_unauth(client):
    reg(client, "target_user", "target@example.com")
    client.cookies.clear()
    r = client.post("/api/v1/users/target_user/follow")
    assert r.status_code == 401

def test_follow_nonexistent(client):
    reg(client, "follower2", "follower2@example.com")
    login(client, "follower2@example.com")
    r = client.post("/api/v1/users/nonexistent_xyz/follow")
    assert r.status_code == 404

def test_followers_following_lists(client):
    reg(client, "user_a", "a2@example.com")
    reg(client, "user_b", "b2@example.com")
    login(client, "a2@example.com")
    client.post("/api/v1/users/user_b/follow")
    r = client.get("/api/v1/users/user_b/followers")
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert len(r.json()["items"]) == 1
    r2 = client.get("/api/v1/users/user_a/following")
    assert r2.json()["total"] == 1

def test_follow_pagination(client):
    reg(client, "pag_followed", "pagfollowed@example.com")
    for i in range(5):
        reg(client, f"follower_{i}", f"follower_{i}@example.com")
        login(client, f"follower_{i}@example.com")
        client.post("/api/v1/users/pag_followed/follow")
    client.cookies.clear()
    login(client, "pagfollowed@example.com")
    r = client.get("/api/v1/users/pag_followed/followers?limit=2&offset=0")
    assert len(r.json()["items"]) == 2
    r2 = client.get("/api/v1/users/pag_followed/followers?limit=2&offset=2")
    assert len(r2.json()["items"]) == 2

def test_follow_isolation(client):
    reg(client, "iso_a", "isoa@example.com")
    reg(client, "iso_b", "isob@example.com")
    login(client, "isoa@example.com")
    client.post("/api/v1/users/iso_b/follow")
    client.cookies.clear()
    reg(client, "iso_c", "isoc@example.com")
    login(client, "isoc@example.com")
    # c follows b, but a's follow still isolated? just check count 2?
    client.post("/api/v1/users/iso_b/follow")
    # followers of b should be 2
    r = client.get("/api/v1/users/iso_b/followers")
    assert r.json()["total"] == 2

# User search
def test_search_users_by_username(client):
    reg(client, "search_alice", "alice_search@example.com")
    login(client, "alice_search@example.com")
    r = client.get("/api/v1/search?q=search_alice&type=users")
    assert r.status_code == 200
    assert any(u["username"] == "search_alice" for u in r.json()["users"])

def test_search_users_display_name(client):
    reg(client, "display_user", "display@example.com")
    # update display name via patch
    login(client, "display@example.com")
    client.patch("/api/v1/users/me", json={"display_name": "UniqueDisplayXYZ"})
    r = client.get("/api/v1/search?q=UniqueDisplayXYZ&type=users")
    assert any(u["username"] == "display_user" for u in r.json()["users"])

def test_search_case_insensitive(client):
    reg(client, "CaseUser", "caseuser@example.com")
    # username lower: caseuser? Actually username pattern allows caps, but stored as is
    r = client.get("/api/v1/search?q=caseuser&type=users")
    assert r.status_code == 200
    # should find regardless of case via lower
    assert len(r.json()["users"]) >= 1

def test_search_pagination_and_empty(client):
    r = client.get("/api/v1/search?q=nonexistent_qwerty_12345&type=users")
    assert r.json()["users"] == []
    r2 = client.get("/api/v1/search?q=&type=users")
    assert r2.status_code == 200
    assert r2.json()["users"] == []

def test_search_too_long(client):
    r = client.get(f"/api/v1/search?q={'x'*101}&type=users")
    assert r.status_code == 422

def test_search_no_sensitive_fields(client):
    reg(client, "sens_user", "sens@example.com")
    r = client.get("/api/v1/search?q=sens_user&type=users")
    for u in r.json()["users"]:
        assert "password_hash" not in str(u).lower()
        assert "email" not in u or u.get("email") is None  # email not returned in search? our search returns no email
        # ensure email not leaked
        assert "sens@example.com" not in str(r.text)

# Post search
def test_search_posts_by_content(client):
    reg(client, "post_searcher", "postsearch@example.com")
    login(client, "postsearch@example.com")
    make_post(client, "unique content XYZ123 for search")
    r = client.get("/api/v1/search?q=XYZ123&type=posts")
    assert any("XYZ123" in p["content"] for p in r.json()["posts"])

def test_search_posts_hashtag(client):
    reg(client, "hashtag_searcher", "hashtagsearch@example.com")
    login(client, "hashtagsearch@example.com")
    make_post(client, "hello #searchtag123")
    r = client.get("/api/v1/search?q=searchtag123&type=posts")
    assert len(r.json()["posts"]) >= 1

def test_search_posts_case_insensitive(client):
    reg(client, "case_post", "casepost@example.com")
    login(client, "casepost@example.com")
    make_post(client, "CaseInsensitiveContent")
    r = client.get("/api/v1/search?q=caseinsensitivecontent&type=posts")
    assert len(r.json()["posts"]) >= 1

# Hashtags
def test_hashtag_existing(client):
    reg(client, "hash_user2", "hash2@example.com")
    login(client, "hash2@example.com")
    make_post(client, "#existinghashtag test")
    r = client.get("/api/v1/hashtags/existinghashtag")
    assert r.status_code == 200
    assert r.json()["name"] == "existinghashtag"

def test_hashtag_case_normalization(client):
    reg(client, "hash_case_user", "hashcase@example.com")
    login(client, "hashcase@example.com")
    make_post(client, "#CaseNormTest unique")
    r = client.get("/api/v1/hashtags/CaseNormTest")
    assert r.status_code == 200
    r2 = client.get("/api/v1/hashtags/casenormtest")
    assert r2.status_code == 200
    assert r.json()["id"] == r2.json()["id"]
    r3 = client.get("/api/v1/hashtags/CASENORMTEST")
    assert r3.status_code == 200
    assert r.json()["id"] == r3.json()["id"]

def test_hashtag_posts(client):
    reg(client, "hash_post_user", "hashpost@example.com")
    login(client, "hashpost@example.com")
    make_post(client, "#mypostshtag content")
    r = client.get("/api/v1/hashtags/mypostshtag/posts")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert "#mypostshtag" in r.json()[0]["content"] or "mypostshtag" in str(r.json()[0]["hashtags"])

def test_hashtag_empty_and_nonexistent(client):
    r = client.get("/api/v1/hashtags/nonexistent_hashtag_xyz_12345")
    assert r.status_code == 404
    r2 = client.get("/api/v1/hashtags/nonexistent_hashtag_xyz_12345/posts")
    assert r2.status_code == 404
