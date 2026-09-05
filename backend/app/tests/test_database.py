"""Database foundation tests — 8 требуемых проверок + доп."""

import uuid
import time

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models.user import User


def test_db_session_creation(db_session):
    # 1. creation
    assert db_session is not None
    # 2. connection (SELECT 1)
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_create_and_read_user(db_session):
    # 3. create + 4. read
    user = User(
        username="testuser",
        email="test@example.com",
        display_name="Test User",
        bio="hello",
    )
    db_session.add(user)
    db_session.flush()

    fetched = db_session.query(User).filter_by(username="testuser").first()
    assert fetched is not None
    assert fetched.email == "test@example.com"
    assert fetched.display_name == "Test User"
    assert fetched.id is not None
    assert isinstance(fetched.id, uuid.UUID)


def test_unique_username_constraint(db_session):
    # 5. unique username
    u1 = User(username="alice", email="alice@example.com")
    db_session.add(u1)
    db_session.flush()

    u2 = User(username="alice", email="alice2@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_unique_email_constraint(db_session):
    # 6. unique email
    u1 = User(username="bob1", email="bob@example.com")
    db_session.add(u1)
    db_session.flush()

    u2 = User(username="bob2", email="bob@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_timestamps(db_session):
    # 7. timestamps are set
    user = User(username="ts_user", email="ts@example.com")
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    assert user.created_at is not None
    assert user.updated_at is not None
    # created_at should be recent (within 10 sec)
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    # SQLite stores naive; compare loosely
    assert (now - user.created_at.replace(tzinfo=datetime.timezone.utc)).total_seconds() < 10


def test_rollback_on_error(db_session):
    # 8. rollback
    user = User(username="rollback_user", email="rollback@example.com")
    db_session.add(user)
    db_session.flush()

    # cause integrity error
    dup = User(username="rollback_user", email="dup@example.com")
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    # original should still exist after rollback? No, rollback undoes transaction including first insert
    # Since fixture transaction is outer, we test that after rollback we can still insert
    user2 = User(username="after_rollback", email="after@example.com")
    db_session.add(user2)
    db_session.flush()
    assert db_session.query(User).filter_by(username="after_rollback").first() is not None


def test_is_active_default(db_session):
    user = User(username="active_test", email="active@example.com")
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    assert user.is_active is True


def test_password_hash_nullable(db_session):
    user = User(username="no_pass", email="nopass@example.com", password_hash=None)
    db_session.add(user)
    db_session.flush()
    fetched = db_session.query(User).filter_by(username="no_pass").first()
    assert fetched.password_hash is None
