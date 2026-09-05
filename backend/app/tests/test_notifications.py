"""Notifications tests — STEP 11."""
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

def test_create_notification_via_follow(client):
    reg(client, "notif_followed", "notiffollowed@example.com")
    reg(client, "notif_follower", "notiffollower@example.com")
    login(client, "notif_follower")
    client.post("/api/v1/users/notif_followed/follow")
    # check recipient's notifications
    client.cookies.clear()
    login(client, "notif_followed")
    r = client.get("/api/v1/notifications")
    assert r.status_code == 200
    data = r.json()
    assert any(n["type"] == "follow" for n in data)

def test_list_own_notifications(client):
    reg(client, "list_user", "listuser@example.com")
    login(client, "listuser@example.com")
    r = client.get("/api/v1/notifications")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_cannot_read_another_users(client):
    reg(client, "victim", "victim@example.com")
    reg(client, "attacker", "attacker@example.com")
    login(client, "victim@example.com")
    # victim gets a follow notification
    client.cookies.clear()
    login(client, "attacker@example.com")
    client.post("/api/v1/users/victim/follow")
    client.cookies.clear()
    login(client, "victim@example.com")
    notifs = client.get("/api/v1/notifications").json()
    assert len(notifs) > 0
    nid = notifs[0]["id"]
    # attacker tries to mark victim's notification
    client.cookies.clear()
    login(client, "attacker@example.com")
    r = client.patch(f"/api/v1/notifications/{nid}/read")
    assert r.status_code in (403, 404)
    r2 = client.delete(f"/api/v1/notifications/{nid}")
    assert r2.status_code in (403, 404)

def test_unread_count(client):
    reg(client, "unread_user", "unread@example.com")
    login(client, "unread@example.com")
    # initially 0
    r = client.get("/api/v1/notifications/unread-count")
    initial = r.json()["count"]
    # create notification via follow from another
    reg(client, "unread_follower", "unreadfollower@example.com")
    client.cookies.clear()
    login(client, "unread_follower")
    client.post("/api/v1/users/unread_user/follow")
    client.cookies.clear()
    login(client, "unread_user")
    r2 = client.get("/api/v1/notifications/unread-count")
    assert r2.json()["count"] == initial + 1

def test_mark_read(client):
    reg(client, "read_user", "readuser@example.com")
    login(client, "readuser@example.com")
    reg(client, "read_follower", "readfollower@example.com")
    client.cookies.clear()
    login(client, "read_follower")
    client.post("/api/v1/users/read_user/follow")
    client.cookies.clear()
    login(client, "read_user")
    notifs = client.get("/api/v1/notifications?unread_only=true").json()
    assert len(notifs) > 0
    nid = notifs[0]["id"]
    r = client.patch(f"/api/v1/notifications/{nid}/read")
    assert r.status_code == 200
    assert r.json()["is_read"] is True
    # unread count should decrease
    r2 = client.get("/api/v1/notifications/unread-count")
    # at least not increased
    assert r2.status_code == 200

def test_mark_all_read(client):
    reg(client, "all_read_user", "allread@example.com")
    login(client, "allread@example.com")
    reg(client, "all_follower1", "allfollower1@example.com")
    client.cookies.clear()
    login(client, "all_follower1")
    client.post("/api/v1/users/all_read_user/follow")
    reg(client, "all_follower2", "allfollower2@example.com")
    client.cookies.clear()
    login(client, "all_follower2")
    client.post("/api/v1/users/all_read_user/follow")
    client.cookies.clear()
    login(client, "all_read_user")
    r = client.post("/api/v1/notifications/read-all")
    assert r.status_code == 200
    r2 = client.get("/api/v1/notifications/unread-count")
    assert r2.json()["count"] == 0

def test_no_self_notification_like(client):
    reg(client, "self_like_user", "selflike@example.com")
    login(client, "self_like_user")
    # create post
    r = client.post("/api/v1/posts", data={"content": "self post"})
    pid = r.json()["id"]
    # like own post
    client.post(f"/api/v1/posts/{pid}/like")
    # should not create notification
    notifs = client.get("/api/v1/notifications").json()
    assert not any(n["type"] == "like" and n["entity_id"] == pid for n in notifs)

def test_notification_generated_on_like(client):
    reg(client, "like_author", "likeauthor@example.com")
    login(client, "like_author")
    pid = client.post("/api/v1/posts", data={"content": "like me"}).json()["id"]
    client.cookies.clear()
    reg(client, "liker", "liker@example.com")
    login(client, "liker@example.com")
    client.post(f"/api/v1/posts/{pid}/like")
    client.cookies.clear()
    login(client, "like_author")
    notifs = client.get("/api/v1/notifications").json()
    assert any(n["type"] == "like" for n in notifs)

def test_notification_generated_on_comment(client):
    reg(client, "comment_author", "commentauthor@example.com")
    login(client, "comment_author")
    pid = client.post("/api/v1/posts", data={"content": "comment me"}).json()["id"]
    client.cookies.clear()
    reg(client, "commenter", "commenter@example.com")
    login(client, "commenter@example.com")
    client.post(f"/api/v1/posts/{pid}/comments", json={"content": "nice!"})
    client.cookies.clear()
    login(client, "comment_author")
    notifs = client.get("/api/v1/notifications").json()
    assert any(n["type"] == "comment" for n in notifs)

def test_pagination(client):
    reg(client, "pag_notif_user", "pagnotif@example.com")
    login(client, "pag_notif_user")
    for i in range(5):
        reg(client, f"pag_follower_{i}", f"pagfollower{i}@example.com")
        client.cookies.clear()
        login(client, f"pag_follower_{i}")
        client.post("/api/v1/users/pag_notif_user/follow")
        client.cookies.clear()
        login(client, "pag_notif_user")
    r = client.get("/api/v1/notifications?limit=2&offset=0")
    assert len(r.json()) == 2
    r2 = client.get("/api/v1/notifications?limit=2&offset=2")
    assert len(r2.json()) == 2
