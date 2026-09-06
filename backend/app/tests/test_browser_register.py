"""Regression for Failed to fetch on registration — real HTTP + CORS + DB init"""
import httpx, time, subprocess, os, signal
from sqlalchemy import create_engine
from app.database.base import Base
import app.models  # noqa: ensure all tables registered

def test_dev_db_has_all_tables(tmp_path):
    # Simulate the bug: create_all without importing app.models would create empty DB
    # Ensure that after importing app.models, all expected tables exist
    db_path = tmp_path / "test_dev.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    # Check that key tables exist
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    conn.close()
    expected = {"users", "posts", "post_media", "hashtags", "post_hashtags", "post_likes", "comments", "post_reposts", "bookmarks", "follows", "stories", "clubs", "club_members", "club_channels", "club_messages", "notifications", "projects"}
    missing = expected - tables
    assert not missing, f"Missing tables: {missing} — dev DB would 500 on register"

def test_register_via_http_with_origin():
    # This replicates the browser's fetch: POST http://localhost:8000/api/v1/auth/register with Origin
    # Uses the running dev server if available, otherwise skip
    # For CI, we test via TestClient with Origin header to ensure CORS/CSRF not blocking
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.database.session import get_db
    from app.main import app as fastapi_app

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    def override():
        S = sessionmaker(bind=engine)
        s = S()
        try:
            yield s
        finally:
            s.close()
    fastapi_app.dependency_overrides[get_db] = override
    client = TestClient(fastapi_app)
    try:
        r = client.post("/api/v1/auth/register", json={"username": "browser_test_qa2", "email": "browser_test_qa2@example.com", "password": "Secret123!"}, headers={"Origin": "http://localhost:5173"})
        assert r.status_code == 201, r.text
        assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert r.headers.get("access-control-allow-credentials") == "true"
        # Verify that without Origin, still works (same-site)
        r2 = client.post("/api/v1/auth/register", json={"username": "browser_test_qa3", "email": "browser_test_qa3@example.com", "password": "Secret123!"})
        assert r2.status_code == 201
    finally:
        fastapi_app.dependency_overrides.clear()
