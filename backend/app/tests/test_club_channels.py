"""Club channels & messages tests — STEP 10."""
import uuid
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

def create_club(client, name="Test Club"):
    return client.post("/api/v1/clubs", json={"name": name})

# Channels
def test_channel_create_list_get(client):
    reg(client, "chan_owner", "chanowner@example.com")
    login(client, "chanowner@example.com")
    slug = create_club(client, "Channel Test Club").json()["slug"]
    r = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general", "description": "main"})
    assert r.status_code == 201, r.text
    assert r.json()["slug"] == "general"
    r2 = client.get(f"/api/v1/clubs/{slug}/channels")
    assert len(r2.json()) == 1
    r3 = client.get(f"/api/v1/clubs/{slug}/channels/general")
    assert r3.status_code == 200

def test_channel_permissions_owner_admin(client):
    reg(client, "chan_owner2", "chanowner2@example.com")
    login(client, "chanowner2@example.com")
    slug = create_club(client, "Perm Club").json()["slug"]
    # owner can create
    assert client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "dev"}).status_code == 201
    # make member
    reg(client, "chan_member", "chanmember@example.com")
    login(client, "chanmember@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    # member cannot create
    r = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "hacker"})
    assert r.status_code == 403
    # promote to admin
    client.cookies.clear()
    login(client, "chan_owner2")
    client.patch(f"/api/v1/clubs/{slug}/members/chan_member/role", json={"role": "admin"})
    client.cookies.clear()
    login(client, "chan_member")
    r2 = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "admin-channel"})
    assert r2.status_code == 201
    # moderator cannot
    client.cookies.clear()
    reg(client, "mod_user2", "moduser2@example.com")
    login(client, "mod_user2")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "chan_owner2")
    client.patch(f"/api/v1/clubs/{slug}/members/mod_user2/role", json={"role": "moderator"})
    client.cookies.clear()
    login(client, "mod_user2")
    assert client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "mod-channel"}).status_code == 403

def test_channel_duplicate_slug(client):
    reg(client, "dup_owner", "dupowner@example.com")
    login(client, "dupowner@example.com")
    slug = create_club(client, "Dup Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    r = client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    # should generate general-1
    assert r.status_code == 201
    assert r.json()["slug"] == "general-1"

def test_channel_update_delete(client):
    reg(client, "upd_owner", "updowner@example.com")
    login(client, "updowner@example.com")
    slug = create_club(client, "Upd Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    r = client.patch(f"/api/v1/clubs/{slug}/channels/general", json={"description": "updated"})
    assert r.status_code == 200
    assert r.json()["description"] == "updated"
    r2 = client.delete(f"/api/v1/clubs/{slug}/channels/general")
    assert r2.status_code == 204
    assert client.get(f"/api/v1/clubs/{slug}/channels/general").status_code == 404

def test_non_member_cannot_access_channels(client):
    reg(client, "no_mem_owner", "nomemowner@example.com")
    login(client, "nomemowner@example.com")
    slug = create_club(client, "NoMem Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    client.cookies.clear()
    reg(client, "outsider", "outsider@example.com")
    login(client, "outsider@example.com")
    assert client.get(f"/api/v1/clubs/{slug}/channels").status_code == 403
    assert client.get(f"/api/v1/clubs/{slug}/channels/general").status_code == 403

def test_channel_belongs_correct_club(client):
    reg(client, "clubA_owner", "clubA@example.com")
    login(client, "clubA@example.com")
    slugA = create_club(client, "Club A").json()["slug"]
    slugB = create_club(client, "Club B").json()["slug"]
    client.post(f"/api/v1/clubs/{slugA}/channels", json={"name": "general"})
    # try to get channel from B using A's slug
    r = client.get(f"/api/v1/clubs/{slugB}/channels/general")
    assert r.status_code == 404

# Messages
def test_message_send_and_list(client):
    reg(client, "msg_owner", "msgowner@example.com")
    login(client, "msgowner@example.com")
    slug = create_club(client, "Msg Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    r = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "Hello FastAPI!"})
    assert r.status_code == 201
    assert r.json()["content"] == "Hello FastAPI!"
    r2 = client.get(f"/api/v1/clubs/{slug}/channels/general/messages")
    assert len(r2.json()) == 1

def test_message_empty_and_long_rejected(client):
    reg(client, "msg_owner2", "msgowner2@example.com")
    login(client, "msgowner2@example.com")
    slug = create_club(client, "Msg Club2").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    assert client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "   "}).status_code == 422
    assert client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "x"*10001}).status_code == 422

def test_message_pagination(client):
    reg(client, "pag_msg_owner", "pagmsgowner@example.com")
    login(client, "pagmsgowner@example.com")
    slug = create_club(client, "Pag Msg Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    for i in range(5):
        client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": f"msg {i}"})
    r = client.get(f"/api/v1/clubs/{slug}/channels/general/messages?limit=2&offset=0")
    assert len(r.json()) == 2
    r2 = client.get(f"/api/v1/clubs/{slug}/channels/general/messages?limit=2&offset=2")
    assert len(r2.json()) == 2

def test_message_edit_own(client):
    reg(client, "edit_msg_owner", "editmsgowner@example.com")
    login(client, "editmsgowner@example.com")
    slug = create_club(client, "Edit Msg Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    mid = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "orig"}).json()["id"]
    r = client.patch(f"/api/v1/clubs/{slug}/channels/general/messages/{mid}", json={"content": "edited"})
    assert r.status_code == 200
    assert r.json()["content"] == "edited"
    assert r.json()["is_edited"] is True

def test_message_cannot_edit_other(client):
    reg(client, "edit_owner3", "editowner3@example.com")
    login(client, "editowner3@example.com")
    slug = create_club(client, "Edit Other Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    mid = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "owner msg"}).json()["id"]
    client.cookies.clear()
    reg(client, "hacker_msg", "hackermsg@example.com")
    login(client, "hacker_msg@example.com")
    client.post(f"/api/v1/clubs/{slug}/join")
    r = client.patch(f"/api/v1/clubs/{slug}/channels/general/messages/{mid}", json={"content": "hacked"})
    assert r.status_code == 403

def test_message_delete_own_and_moderator(client):
    reg(client, "del_owner4", "delowner4@example.com")
    login(client, "delowner4@example.com")
    slug = create_club(client, "Del Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    mid = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "to delete"}).json()["id"]
    # owner delete own
    r = client.delete(f"/api/v1/clubs/{slug}/channels/general/messages/{mid}")
    assert r.status_code == 204
    # create again for moderator test
    mid2 = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "owner msg2"}).json()["id"]
    reg(client, "mod_del", "moddel@example.com")
    login(client, "mod_del")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "del_owner4")
    client.patch(f"/api/v1/clubs/{slug}/members/mod_del/role", json={"role": "moderator"})
    client.cookies.clear()
    login(client, "mod_del")
    r2 = client.delete(f"/api/v1/clubs/{slug}/channels/general/messages/{mid2}")
    assert r2.status_code == 204
    # member cannot delete other
    reg(client, "plain_del", "plaindel@example.com")
    login(client, "plain_del")
    client.post(f"/api/v1/clubs/{slug}/join")
    client.cookies.clear()
    login(client, "del_owner4")
    mid3 = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "owner msg3"}).json()["id"]
    client.cookies.clear()
    login(client, "plain_del")
    assert client.delete(f"/api/v1/clubs/{slug}/channels/general/messages/{mid3}").status_code == 403

def test_non_member_cannot_send(client):
    reg(client, "no_send_owner", "nosendowner@example.com")
    login(client, "nosendowner@example.com")
    slug = create_club(client, "NoSend Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    client.cookies.clear()
    reg(client, "outsider2", "outsider2@example.com")
    login(client, "outsider2@example.com")
    assert client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "hack"}).status_code == 403
    assert client.get(f"/api/v1/clubs/{slug}/channels/general/messages").status_code == 403

# IDOR
def test_cross_club_channel_access(client):
    reg(client, "cross_ownerA", "crossA@example.com")
    login(client, "crossA@example.com")
    slugA = create_club(client, "Cross A").json()["slug"]
    slugB = create_club(client, "Cross B").json()["slug"]
    client.post(f"/api/v1/clubs/{slugA}/channels", json={"name": "secret"})
    # user in A tries to get channel via B
    r = client.get(f"/api/v1/clubs/{slugB}/channels/secret")
    assert r.status_code == 404
    # messages cross
    reg(client, "cross_user", "crossuser@example.com")
    login(client, "cross_user@example.com")
    client.post(f"/api/v1/clubs/{slugA}/join")
    # channel secret is in A, try to send via B — should be blocked (404 channel not found or 403 not member)
    assert client.post(f"/api/v1/clubs/{slugB}/channels/secret/messages", json={"content": "hack"}).status_code in (404, 403)

def test_forged_channel_message_relationship(client):
    reg(client, "forge_owner", "forgeowner@example.com")
    login(client, "forgeowner@example.com")
    slug = create_club(client, "Forge Club").json()["slug"]
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "general"})
    client.post(f"/api/v1/clubs/{slug}/channels", json={"name": "random"})
    mid = client.post(f"/api/v1/clubs/{slug}/channels/general/messages", json={"content": "hello"}).json()["id"]
    # try to edit via wrong channel slug
    r = client.patch(f"/api/v1/clubs/{slug}/channels/random/messages/{mid}", json={"content": "hacked"})
    assert r.status_code == 404
