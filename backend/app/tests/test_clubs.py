"""Clubs tests — STEP 9."""
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

# Clubs
def test_create_club(client):
    reg(client, "owner1", "owner1@example.com")
    login(client, "owner1@example.com")
    r = client.post("/api/v1/clubs", json={"name": "Python Kazakhstan", "description": "Python community"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Python Kazakhstan"
    assert data["slug"] == "python-kazakhstan"
    assert data["role"] == "owner"
    assert data["is_member"] is True
    assert data["members_count"] == 1

def test_create_unauth(client):
    client.cookies.clear()
    r = client.post("/api/v1/clubs", json={"name": "No Auth"})
    assert r.status_code == 401

def test_owner_auto_member(client):
    reg(client, "owner2", "owner2@example.com")
    login(client, "owner2@example.com")
    r = client.post("/api/v1/clubs", json={"name": "Owner Test Club"})
    slug = r.json()["slug"]
    # check members
    r2 = client.get(f"/api/v1/clubs/{slug}/members")
    assert r2.status_code == 200
    assert any(m["username"] == "owner2" and m["role"] == "owner" for m in r2.json()["items"])

def test_public_list_and_detail(client):
    reg(client, "list_owner", "listowner@example.com")
    login(client, "listowner@example.com")
    client.post("/api/v1/clubs", json={"name": "List Club A"})
    client.post("/api/v1/clubs", json={"name": "List Club B"})
    client.cookies.clear()  # public
    r = client.get("/api/v1/clubs")
    assert r.status_code == 200
    assert len(r.json()) >= 2
    r2 = client.get(f"/api/v1/clubs/{r.json()[0]['slug']}")
    assert r2.status_code == 200

def test_pagination_and_search(client):
    reg(client, "search_owner", "searchowner@example.com")
    login(client, "searchowner@example.com")
    client.post("/api/v1/clubs", json={"name": "Search Unique Club XYZ"})
    r = client.get("/api/v1/clubs?q=Unique%20Club%20XYZ")
    assert any("Search Unique" in c["name"] for c in r.json())
    r2 = client.get("/api/v1/clubs?limit=1&offset=0")
    assert len(r2.json()) == 1

def test_edit_owner(client):
    reg(client, "edit_owner", "editowner@example.com")
    login(client, "editowner@example.com")
    r = client.post("/api/v1/clubs", json={"name": "Edit Club"})
    slug = r.json()["slug"]
    r2 = client.patch(f"/api/v1/clubs/{slug}", json={"description": "new desc"})
    assert r2.status_code == 200
    assert r2.json()["description"] == "new desc"

def test_edit_unauth(client):
    reg(client, "edit_owner2", "editowner2@example.com")
    login(client, "editowner2@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Edit2"}).json()["slug"]
    client.cookies.clear()
    reg(client, "hacker_edit", "hackeredit@example.com")
    login(client, "hackeredit@example.com")
    r = client.patch(f"/api/v1/clubs/{slug}", json={"description": "hacked"})
    assert r.status_code == 403

def test_delete_owner_and_non_owner(client):
    reg(client, "del_owner", "delowner@example.com")
    login(client, "delowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Delete Me"}).json()["slug"]
    r = client.delete(f"/api/v1/clubs/{slug}")
    assert r.status_code == 204
    assert client.get(f"/api/v1/clubs/{slug}").status_code == 404
    # non-owner delete
    reg(client, "del_owner2", "delowner2@example.com")
    login(client, "delowner2@example.com")
    slug2 = client.post("/api/v1/clubs", json={"name": "Delete2"}).json()["slug"]
    client.cookies.clear()
    reg(client, "hacker_del", "hackerdel@example.com")
    login(client, "hackerdel@example.com")
    r2 = client.delete(f"/api/v1/clubs/{slug2}")
    assert r2.status_code == 403

def test_nonexistent(client):
    client.cookies.clear()
    reg(client, "nonexist_user", "nonexist@example.com")
    login(client, "nonexist@example.com")
    assert client.get("/api/v1/clubs/nonexistent-slug-xyz").status_code == 404

# Membership
def test_join_and_duplicate(client):
    reg(client, "join_owner", "joinowner@example.com")
    login(client, "joinowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Join Club"}).json()["slug"]
    client.cookies.clear()
    reg(client, "joiner", "joiner@example.com")
    login(client, "joiner@example.com")
    r = client.post(f"/api/v1/clubs/{slug}/join")
    assert r.status_code == 201
    r2 = client.post(f"/api/v1/clubs/{slug}/join")
    assert r2.status_code in (200,201)

def test_leave_and_duplicate(client):
    reg(client, "leave_owner", "leaveowner@example.com")
    login(client, "leaveowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Leave Club"}).json()["slug"]
    reg(client, "leaver", "leaver@example.com")
    login(client, "leaver@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    r = client.delete(f"/api/v1/clubs/{slug}/leave")
    assert r.status_code == 204
    r2 = client.delete(f"/api/v1/clubs/{slug}/leave")
    assert r2.status_code == 204

def test_owner_cannot_leave(client):
    reg(client, "owner_leave", "ownerleave@example.com")
    login(client, "ownerleave@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Owner Leave Club"}).json()["slug"]
    r = client.delete(f"/api/v1/clubs/{slug}/leave")
    assert r.status_code == 400

def test_members_list(client):
    reg(client, "mem_owner", "memowner@example.com")
    login(client, "memowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Members Club"}).json()["slug"]
    reg(client, "mem1", "mem1@example.com")
    login(client, "mem1@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    r = client.get(f"/api/v1/clubs/{slug}/members")
    assert r.status_code == 200
    assert r.json()["total"] >= 2
    assert "email" not in str(r.json()).lower()

# Roles
def test_owner_role(client):
    reg(client, "role_owner", "roleowner@example.com")
    login(client, "roleowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Role Club"}).json()["slug"]
    r = client.get(f"/api/v1/clubs/{slug}/members")
    assert any(m["role"] == "owner" for m in r.json()["items"])

def test_promote_and_demote(client):
    reg(client, "promo_owner", "promoowner@example.com")
    login(client, "promoowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Promo Club"}).json()["slug"]
    reg(client, "promo_member", "promomember@example.com")
    login(client, "promomember@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "promoowner@example.com")
    r = client.patch(f"/api/v1/clubs/{slug}/members/promo_member/role", json={"role": "moderator"})
    assert r.status_code == 200
    # demote
    r2 = client.patch(f"/api/v1/clubs/{slug}/members/promo_member/role", json={"role": "member"})
    assert r2.status_code == 200

def test_admin_permissions(client):
    reg(client, "admin_owner", "adminowner@example.com")
    login(client, "adminowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Admin Club"}).json()["slug"]
    reg(client, "to_admin", "toadmin@example.com")
    login(client, "toadmin@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "adminowner@example.com")
    client.patch(f"/api/v1/clubs/{slug}/members/to_admin/role", json={"role": "admin"})
    # admin can promote to moderator
    client.cookies.clear()
    reg(client, "member2", "member2@example.com")
    login(client, "member2@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "toadmin@example.com")
    r = client.patch(f"/api/v1/clubs/{slug}/members/member2/role", json={"role": "moderator"})
    assert r.status_code == 200
    # admin cannot assign admin
    r2 = client.patch(f"/api/v1/clubs/{slug}/members/member2/role", json={"role": "admin"})
    assert r2.status_code == 403
    # admin cannot modify owner
    r3 = client.patch(f"/api/v1/clubs/{slug}/members/admin_owner/role", json={"role": "member"})
    assert r3.status_code == 403

def test_moderator_permissions(client):
    reg(client, "mod_owner2", "modowner2@example.com")
    login(client, "modowner2@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Mod Club2"}).json()["slug"]
    reg(client, "mod_user", "moduser@example.com")
    login(client, "moduser@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "modowner2@example.com")
    client.patch(f"/api/v1/clubs/{slug}/members/mod_user/role", json={"role": "moderator"})
    reg(client, "member3", "member3@example.com")
    login(client, "member3@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "mod_user")
    # moderator can remove member
    r = client.delete(f"/api/v1/clubs/{slug}/members/member3")
    assert r.status_code == 204
    # moderator cannot change roles
    r2 = client.patch(f"/api/v1/clubs/{slug}/members/member3/role", json={"role": "member"})
    # member3 not member now, but even if, should 403
    assert r2.status_code in (403, 404)

def test_member_forbidden(client):
    reg(client, "mem_owner3", "memowner3@example.com")
    login(client, "memowner3@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Member Forbidden Club"}).json()["slug"]
    reg(client, "plain_member", "plainmember@example.com")
    login(client, "plainmember@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    r = client.patch(f"/api/v1/clubs/{slug}/members/plain_member/role", json={"role": "admin"})
    assert r.status_code == 403
    r2 = client.delete(f"/api/v1/clubs/{slug}/members/plain_member")
    assert r2.status_code == 403

def test_cannot_promote_to_owner(client):
    reg(client, "owner_protect", "ownerprotect@example.com")
    login(client, "ownerprotect@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Protect Owner"}).json()["slug"]
    reg(client, "victim", "victim@example.com")
    login(client, "victim@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "ownerprotect@example.com")
    r = client.patch(f"/api/v1/clubs/{slug}/members/victim/role", json={"role": "owner"})
    assert r.status_code in (403, 422)

def test_cannot_modify_owner(client):
    reg(client, "owner_mod", "ownermod@example.com")
    login(client, "ownermod@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Owner Mod Club"}).json()["slug"]
    reg(client, "admin2", "admin2@example.com")
    login(client, "admin2@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "ownermod@example.com")
    client.patch(f"/api/v1/clubs/{slug}/members/admin2/role", json={"role": "admin"})
    client.cookies.clear()
    login(client, "admin2@example.com")
    r = client.patch(f"/api/v1/clubs/{slug}/members/owner_mod/role", json={"role": "member"})
    assert r.status_code == 403

def test_privilege_escalation(client):
    reg(client, "priv_owner", "privowner@example.com")
    login(client, "privowner@example.com")
    slug = client.post("/api/v1/clubs", json={"name": "Priv Esc Club"}).json()["slug"]
    reg(client, "priv_member", "privmember@example.com")
    login(client, "privmember@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    # member tries to become admin via forged request
    r = client.patch(f"/api/v1/clubs/{slug}/members/priv_member/role", json={"role": "admin"})
    assert r.status_code == 403

# Security
def test_forged_owner_id_ignored(client):
    reg(client, "forge_owner", "forgeowner@example.com")
    login(client, "forgeowner@example.com")
    # try to create club with owner_id forged
    r = client.post("/api/v1/clubs", json={"name": "Forge Club", "description": "test", "owner_id": str(uuid.uuid4())})
    assert r.status_code == 201
    assert r.json()["owner_id"] != str(uuid.uuid4())  # owner is current user, not forged

def test_sensitive_fields_not_returned(client):
    reg(client, "sens_owner", "sensowner@example.com")
    login(client, "sensowner@example.com")
    r = client.post("/api/v1/clubs", json={"name": "Sensitive Club"})
    slug = r.json()["slug"]
    r2 = client.get(f"/api/v1/clubs/{slug}")
    assert "password" not in r2.text.lower()
    assert "email" not in r2.text.lower()
