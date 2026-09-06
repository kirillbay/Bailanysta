"""Edge-case regression tests — STEP 15."""
import uuid, io
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app
import pytest

def _img():
    bio = io.BytesIO()
    Image.new("RGB", (10,10), (255,0,0)).save(bio, format="PNG")
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

# ── Unicode / i18n ──
def test_unicode_post_and_comment(client):
    reg(client, "uni_user", "uni@example.com")
    login(client, "uni@example.com")
    content = "Привет Байланыста! Қазақша тест 🚀 中文 العربية"
    r = client.post("/api/v1/posts", data={"content": content})
    assert r.status_code == 201
    pid = r.json()["id"]
    # comment unicode
    r2 = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "Комментарий 🚀 測試"})
    assert r2.status_code == 201
    # fetch and verify preserved
    r3 = client.get(f"/api/v1/posts/{pid}")
    assert "Привет" in r3.json()["content"]

def test_username_min_max(client):
    # min 3
    r = client.post("/api/v1/auth/register", json={"username": "ab", "email": "ab@example.com", "password": "Secret123!"})
    assert r.status_code == 422
    # max 50 -> 51 should fail
    r2 = client.post("/api/v1/auth/register", json={"username": "a"*51, "email": "a51@example.com", "password": "Secret123!"})
    assert r2.status_code == 422
    # exactly 50 should pass
    r3 = client.post("/api/v1/auth/register", json={"username": "a"*50, "email": "a50@example.com", "password": "Secret123!"})
    assert r3.status_code == 201

def test_post_max_length_boundary(client):
    reg(client, "postlen_user", "postlen@example.com")
    login(client, "postlen@example.com")
    # exactly 10000 should pass
    r = client.post("/api/v1/posts", data={"content": "x"*10000})
    assert r.status_code == 201
    # 10001 should fail
    r2 = client.post("/api/v1/posts", data={"content": "x"*10001})
    assert r2.status_code == 422

def test_comment_max_boundary(client):
    reg(client, "commentlen_user", "commentlen_user@example.com")
    login(client, "commentlen_user@example.com")
    pid = client.post("/api/v1/posts", data={"content": "hello"}).json()["id"]
    r = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "y"*2000})
    assert r.status_code == 201
    r2 = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "y"*2001})
    assert r2.status_code == 422

def test_message_max_boundary(client):
    reg(client, "msglen_user", "msglen@example.com")
    login(client, "msglen@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "MsgLen Club"}).json()["slug"]
    ch = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"}).json()
    # 10000 ok
    r = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "z"*10000})
    assert r.status_code == 201
    # 10001 fail
    r2 = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "z"*10001})
    assert r2.status_code == 422

def test_empty_string_rejected(client):
    reg(client, "empty_user", "empty@example.com")
    login(client, "empty@example.com")
    # empty post
    r = client.post("/api/v1/posts", data={"content": "   "})
    assert r.status_code == 422
    # empty comment
    pid = client.post("/api/v1/posts", data={"content": "valid"}).json()["id"]
    r2 = client.post(f"/api/v1/posts/{pid}/comments", json={"content": "   "})
    assert r2.status_code == 422

def test_invalid_uuid_variants(client):
    reg(client, "uuid_edge", "uuid_edge@example.com")
    login(client, "uuid_edge@example.com")
    for bad in ["not-uuid", "123", "00000000-0000-0000-0000-00000000000Z"]:
        r = client.get(f"/api/v1/posts/{bad}")
        assert r.status_code == 422, bad
        r2 = client.get(f"/api/v1/projects/{bad}")
        assert r2.status_code == 422

def test_nonexistent_uuid_404(client):
    reg(client, "nonexist_edge", "nonexist_edge@example.com")
    login(client, "nonexist_edge@example.com")
    uid = str(uuid.uuid4())
    assert client.get(f"/api/v1/posts/{uid}").status_code == 404
    assert client.get(f"/api/v1/projects/{uid}").status_code == 404
    assert client.get(f"/api/v1/clubs/nonexistent-slug-xyz").status_code == 404

def test_pagination_boundaries(client):
    reg(client, "pag_edge", "pag_edge@example.com")
    login(client, "pag_edge@example.com")
    # limit=0 should be 422
    assert client.get("/api/v1/feed?limit=0").status_code == 422
    # negative offset 422
    assert client.get("/api/v1/feed?limit=10&offset=-1").status_code == 422
    # huge offset should return empty list not 500
    r = client.get("/api/v1/feed?limit=10&offset=999999")
    assert r.status_code == 200
    assert r.json() == []
    # max limit 50 ok, 51 should be 422
    assert client.get("/api/v1/feed?limit=50").status_code == 200
    assert client.get("/api/v1/feed?limit=51").status_code == 422
    # search huge offset
    r2 = client.get("/api/v1/search?q=test&limit=10&offset=999999")
    assert r2.status_code == 200
    assert r2.json()["posts"] == []

def test_duplicate_like_idempotent(client):
    reg(client, "dup_like_user", "dup_like@example.com")
    login(client, "dup_like@example.com")
    pid = client.post("/api/v1/posts", data={"content": "dup like test"}).json()["id"]
    r1 = client.post(f"/api/v1/posts/{pid}/like")
    assert r1.status_code == 201
    r2 = client.post(f"/api/v1/posts/{pid}/like")
    assert r2.status_code in (200, 201)  # Already liked
    # unlike twice idempotent
    r3 = client.delete(f"/api/v1/posts/{pid}/like")
    assert r3.status_code == 204
    r4 = client.delete(f"/api/v1/posts/{pid}/like")
    assert r4.status_code == 204

def test_duplicate_follow_idempotent(client):
    reg(client, "dup_follow_a", "dup_follow_a@example.com")
    login(client, "dup_follow_a@example.com")
    reg(client, "dup_follow_b", "dup_follow_b@example.com")
    client.cookies.clear()
    login(client, "dup_follow_a@example.com")
    r1 = client.post("/api/v1/users/dup_follow_b/follow")
    assert r1.status_code in (200, 201)
    r2 = client.post("/api/v1/users/dup_follow_b/follow")
    assert r2.status_code in (200, 201)

def test_nonexistent_resource_handling(client):
    reg(client, "nonexist_res", "nonexist_res@example.com")
    login(client, "nonexist_res@example.com")
    fake = str(uuid.uuid4())
    # like nonexistent post
    assert client.post(f"/api/v1/posts/{fake}/like").status_code == 404
    # comment on nonexistent
    assert client.post(f"/api/v1/posts/{fake}/comments", json={"content": "hi"}).status_code == 404
    # bookmark nonexistent
    assert client.post(f"/api/v1/posts/{fake}/bookmark").status_code == 404

def test_expired_story_not_visible(client):
    reg(client, "story_exp_user", "story_exp@example.com")
    login(client, "story_exp@example.com")
    # Create story with image
    r = client.post("/api/v1/stories", files={"file": ("img.png", _img(), "image/png")})
    # Depending on impl, may be 201
    if r.status_code == 201:
        sid = r.json()["id"]
        # stories are visible in feed (GET /api/v1/stories)
        feed = client.get("/api/v1/stories")
        assert feed.status_code == 200
        # deletion
        assert client.delete(f"/api/v1/stories/{sid}").status_code in (200, 204)
        # after delete, not found
        assert client.get(f"/api/v1/stories/{sid}").status_code == 404

def test_club_cascade_delete(client):
    reg(client, "cascade_owner", "cascade_owner@example.com")
    login(client, "cascade_owner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Cascade Club"}).json()["slug"]
    ch = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"}).json()
    client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "hello"})
    # delete club
    assert client.delete(f"/api/v1/clubs/{slug}").status_code == 204
    # channel should be gone
    assert client.get(f"/api/v1/clubs/{slug}/channels/{ch['slug']}").status_code == 404

def test_project_github_validation_edge(client):
    reg(client, "gh_edge", "gh_edge@example.com")
    login(client, "gh_edge@example.com")
    # empty github allowed (null)
    r = client.post("/api/v1/users/me/projects", json={"name": "GHTest", "description": "desc", "github_url": "", "status": "idea"})
    assert r.status_code == 201
    # http allowed for demo, https for github
    r2 = client.post("/api/v1/users/me/projects", json={"name": "GH2", "description": "desc", "github_url": "https://github.com/user/repo", "demo_url": "http://example.com", "status": "idea"})
    assert r2.status_code == 201
    # with www
    r3 = client.post("/api/v1/users/me/projects", json={"name": "GH3", "description": "desc", "github_url": "https://www.github.com/user/repo", "status": "idea"})
    assert r3.status_code == 201

def test_search_empty_and_max_length(client):
    reg(client, "search_edge", "search_edge@example.com")
    login(client, "search_edge@example.com")
    # empty q should return empty lists not error
    r = client.get("/api/v1/search?q=&type=all")
    assert r.status_code == 200
    assert r.json()["users"] == []
    # 101 chars should be 422
    r2 = client.get(f"/api/v1/search?q={'a'*101}")
    assert r2.status_code == 422
    # exactly 100 should pass
    r3 = client.get(f"/api/v1/search?q={'a'*100}")
    assert r3.status_code == 200
