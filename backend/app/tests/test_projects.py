"""Projects showcase tests — STEP 12."""
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

# CRUD
def test_create_project(client):
    reg(client, "proj_owner1", "proj_owner1@example.com")
    login(client, "proj_owner1@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "Bailanysta", "description": "Social platform", "technologies": ["Python", "FastAPI"], "github_url": "https://github.com/test/repo", "demo_url": "https://example.com", "status": "in_progress"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Bailanysta"
    assert data["technologies"] == ["Python", "FastAPI"]
    assert data["github_url"] == "https://github.com/test/repo"
    assert data["status"] == "in_progress"
    assert data["owner"]["username"] == "proj_owner1"
    assert "password" not in r.text.lower()

def test_list_own_and_public(client):
    reg(client, "proj_owner2", "proj_owner2@example.com")
    login(client, "proj_owner2@example.com")
    client.post("/api/v1/users/me/projects", json={"name": "MyProj", "description": "desc", "technologies": ["React"], "status": "idea"})
    r = client.get("/api/v1/users/me/projects")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    # public
    client.cookies.clear()
    r2 = client.get("/api/v1/users/proj_owner2/projects")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1
    # nonexistent user
    r3 = client.get("/api/v1/users/nonexistent_xyz/projects")
    assert r3.status_code == 404

def test_get_project(client):
    reg(client, "proj_owner3", "proj_owner3@example.com")
    login(client, "proj_owner3@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "GetProj", "description": "desc", "status": "completed"}).json()["id"]
    client.cookies.clear()
    r = client.get(f"/api/v1/projects/{pid}")
    assert r.status_code == 200
    assert r.json()["name"] == "GetProj"
    assert client.get(f"/api/v1/projects/{str(uuid.uuid4())}").status_code == 404

def test_update_own(client):
    reg(client, "proj_owner4", "proj_owner4@example.com")
    login(client, "proj_owner4@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "OldName", "description": "old", "status": "idea"}).json()["id"]
    r = client.patch(f"/api/v1/users/me/projects/{pid}", json={"name": "NewName", "status": "completed"})
    assert r.status_code == 200
    assert r.json()["name"] == "NewName"
    assert r.json()["status"] == "completed"

def test_delete_own(client):
    reg(client, "proj_owner5", "proj_owner5@example.com")
    login(client, "proj_owner5@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "DelProj", "description": "desc", "status": "idea"}).json()["id"]
    r = client.delete(f"/api/v1/users/me/projects/{pid}")
    assert r.status_code == 204
    assert client.get(f"/api/v1/projects/{pid}").status_code == 404

def test_pagination_and_ordering(client):
    reg(client, "proj_pag", "proj_pag@example.com")
    login(client, "proj_pag@example.com")
    for i in range(3):
        client.post("/api/v1/users/me/projects", json={"name": f"P{i}", "description": "desc", "status": "idea"})
    r = client.get("/api/v1/users/proj_pag/projects?limit=2&offset=0")
    assert len(r.json()) == 2
    r2 = client.get("/api/v1/users/proj_pag/projects?limit=2&offset=2")
    assert len(r2.json()) >= 1

# Validation
def test_empty_name(client):
    reg(client, "proj_val1", "proj_val1@example.com")
    login(client, "proj_val1@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "", "description": "desc", "status": "idea"})
    assert r.status_code == 422
    r2 = client.post("/api/v1/users/me/projects", json={"name": "   ", "description": "desc", "status": "idea"})
    assert r2.status_code == 422

def test_too_long_name(client):
    reg(client, "proj_val2", "proj_val2@example.com")
    login(client, "proj_val2@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "A"*151, "description": "desc", "status": "idea"})
    assert r.status_code == 422

def test_too_long_description(client):
    reg(client, "proj_val3", "proj_val3@example.com")
    login(client, "proj_val3@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "A"*2001, "status": "idea"})
    assert r.status_code == 422

def test_invalid_status(client):
    reg(client, "proj_val4", "proj_val4@example.com")
    login(client, "proj_val4@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "status": "wrong"})
    assert r.status_code == 422

def test_invalid_technology_too_long(client):
    reg(client, "proj_val5", "proj_val5@example.com")
    login(client, "proj_val5@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "technologies": ["A"*51], "status": "idea"})
    assert r.status_code == 422

def test_too_many_technologies(client):
    reg(client, "proj_val6", "proj_val6@example.com")
    login(client, "proj_val6@example.com")
    techs = [f"T{i}" for i in range(21)]
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "technologies": techs, "status": "idea"})
    assert r.status_code == 422

def test_duplicate_technologies_dedup(client):
    reg(client, "proj_dup", "proj_dup@example.com")
    login(client, "proj_dup@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "DupTech", "description": "desc", "technologies": ["Python", "python", "  Python "], "status": "idea"})
    assert r.status_code == 201
    assert len(r.json()["technologies"]) == 1

def test_invalid_url_scheme(client):
    reg(client, "proj_url1", "proj_url1@example.com")
    login(client, "proj_url1@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "github_url": "javascript:alert(1)", "status": "idea"})
    assert r.status_code == 422
    r2 = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "demo_url": "data:text/html,hi", "status": "idea"})
    assert r2.status_code == 422
    r3 = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "demo_url": "file:///etc/passwd", "status": "idea"})
    assert r3.status_code == 422

def test_invalid_github_host(client):
    reg(client, "proj_url2", "proj_url2@example.com")
    login(client, "proj_url2@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "github_url": "https://gitlab.com/test/repo", "status": "idea"})
    assert r.status_code == 422
    r2 = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "github_url": "https://evil.com/repo", "status": "idea"})
    assert r2.status_code == 422
    # valid github with www
    r3 = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "github_url": "https://www.github.com/test/repo", "status": "idea"})
    assert r3.status_code == 201

# Security
def test_unauth_create(client):
    client.cookies.clear()
    r = client.post("/api/v1/users/me/projects", json={"name": "N", "description": "desc", "status": "idea"})
    assert r.status_code == 401

def test_cannot_update_other(client):
    reg(client, "proj_a", "proj_a@example.com")
    login(client, "proj_a@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "Aproj", "description": "desc", "status": "idea"}).json()["id"]
    client.cookies.clear()
    reg(client, "proj_b", "proj_b@example.com")
    login(client, "proj_b@example.com")
    r = client.patch(f"/api/v1/users/me/projects/{pid}", json={"name": "Hacked"})
    assert r.status_code == 403
    # also cannot delete
    r2 = client.delete(f"/api/v1/users/me/projects/{pid}")
    assert r2.status_code == 403

def test_cannot_upload_other(client):
    reg(client, "proj_u1", "proj_u1@example.com")
    login(client, "proj_u1@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "Uproj", "description": "desc", "status": "idea"}).json()["id"]
    client.cookies.clear()
    reg(client, "proj_u2", "proj_u2@example.com")
    login(client, "proj_u2@example.com")
    r = client.post(f"/api/v1/users/me/projects/{pid}/image", files={"file": ("test.png", _img(), "image/png")})
    assert r.status_code == 403

def test_forged_owner_ignored(client):
    reg(client, "proj_forge", "proj_forge@example.com")
    login(client, "proj_forge@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "Forge", "description": "desc", "status": "idea", "owner_id": str(uuid.uuid4())})
    assert r.status_code == 201
    # owner_id is current user, not forged
    assert r.json()["owner"]["username"] == "proj_forge"

def test_sensitive_not_exposed(client):
    reg(client, "proj_sens", "proj_sens@example.com")
    login(client, "proj_sens@example.com")
    r = client.post("/api/v1/users/me/projects", json={"name": "Sens", "description": "desc", "status": "idea"})
    assert "password" not in r.text.lower()
    assert "secret" not in r.text.lower()

def test_image_upload_success(client):
    reg(client, "proj_img", "proj_img@example.com")
    login(client, "proj_img@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "ImgProj", "description": "desc", "status": "idea"}).json()["id"]
    r = client.post(f"/api/v1/users/me/projects/{pid}/image", files={"file": ("test.png", _img(), "image/png")})
    assert r.status_code == 200, r.text
    assert r.json()["image_url"] is not None
    assert "/uploads/projects/" in r.json()["image_url"]

def test_image_invalid_type(client):
    reg(client, "proj_img2", "proj_img2@example.com")
    login(client, "proj_img2@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "Img2", "description": "desc", "status": "idea"}).json()["id"]
    r = client.post(f"/api/v1/users/me/projects/{pid}/image", files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
    assert r.status_code == 415

def test_image_unauth(client):
    reg(client, "proj_img3", "proj_img3@example.com")
    login(client, "proj_img3@example.com")
    pid = client.post("/api/v1/users/me/projects", json={"name": "Img3", "description": "desc", "status": "idea"}).json()["id"]
    client.cookies.clear()
    r = client.post(f"/api/v1/users/me/projects/{pid}/image", files={"file": ("test.png", _img(), "image/png")})
    assert r.status_code == 401

# Search
def test_search_projects(client):
    reg(client, "proj_search", "proj_search@example.com")
    login(client, "proj_search@example.com")
    client.post("/api/v1/users/me/projects", json={"name": "UniqueSearchProjXYZ", "description": "AI analyzer", "technologies": ["Python"], "status": "idea"})
    client.cookies.clear()
    r = client.get("/api/v1/search?q=UniqueSearchProjXYZ&type=projects")
    assert r.status_code == 200
    assert any("UniqueSearchProjXYZ" in p["name"] for p in r.json()["projects"])
    r2 = client.get("/api/v1/search?q=AI%20analyzer&type=projects")
    assert any("UniqueSearchProjXYZ" in p["name"] for p in r2.json()["projects"])
    r3 = client.get("/api/v1/search?q=Python&type=projects")
    assert r3.status_code == 200
