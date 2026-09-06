"""Test CORS preflight for production frontend origin"""
import os
import importlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
import app.models

def _client_with_cors(origins: str):
    # Save original
    orig_cors = os.environ.get("CORS_ORIGINS")
    orig_env = os.environ.get("APP_ENV")
    orig_secret = os.environ.get("SECRET_KEY")
    os.environ["CORS_ORIGINS"] = origins
    os.environ["APP_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret-key-1234567890abcdef1234567890abcdef"
    # Reload settings and dependent modules
    import app.core.config
    importlib.reload(app.core.config)
    from app.core.config import settings
    import app.core.security
    importlib.reload(app.core.security)
    import app.api.v1.auth
    importlib.reload(app.api.v1.auth)
    # Need to reload main to pick up new settings
    import app.main
    importlib.reload(app.main)
    from app.main import app as fastapi_app
    from app.database.session import get_db

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
    return client, fastapi_app, engine

def test_cors_production_origin():
    orig_cors = os.environ.get("CORS_ORIGINS")
    orig_env = os.environ.get("APP_ENV")
    orig_secret = os.environ.get("SECRET_KEY")
    client, app, engine = _client_with_cors("https://bailanysta-front.onrender.com")
    try:
        headers = {
            "Origin": "https://bailanysta-front.onrender.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        r = client.options("/api/v1/auth/demo", headers=headers)
        assert r.status_code == 200, f"Preflight failed: {r.status_code} {r.text} headers {r.headers}"
        assert r.headers.get("access-control-allow-origin") == "https://bailanysta-front.onrender.com"
        assert r.headers.get("access-control-allow-credentials") == "true"
        # Actual POST should also have CORS headers
        r2 = client.post("/api/v1/auth/demo", json={}, headers={"Origin": "https://bailanysta-front.onrender.com"})
        assert r2.status_code == 200
        assert r2.headers.get("access-control-allow-origin") == "https://bailanysta-front.onrender.com"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        # Restore env
        if orig_cors is not None:
            os.environ["CORS_ORIGINS"] = orig_cors
        else:
            os.environ.pop("CORS_ORIGINS", None)
        if orig_env is not None:
            os.environ["APP_ENV"] = orig_env
        else:
            os.environ.pop("APP_ENV", None)
        if orig_secret is not None:
            os.environ["SECRET_KEY"] = orig_secret
        else:
            os.environ.pop("SECRET_KEY", None)
        import app.core.config
        importlib.reload(app.core.config)
        import app.core.security
        importlib.reload(app.core.security)
        import app.api.v1.auth
        importlib.reload(app.api.v1.auth)
        import app.main
        importlib.reload(app.main)

def test_cors_with_trailing_slash_and_quotes():
    # Test that CORS handles trailing slash and quotes gracefully (common Render misconfig)
    orig_cors = os.environ.get("CORS_ORIGINS")
    orig_env = os.environ.get("APP_ENV")
    orig_secret = os.environ.get("SECRET_KEY")
    for origins in [
        "https://bailanysta-front.onrender.com/",
        '"https://bailanysta-front.onrender.com"',
        "'https://bailanysta-front.onrender.com'",
        "https://bailanysta-front.onrender.com, http://localhost:5173",
    ]:
        client, app, engine = _client_with_cors(origins)
        try:
            headers = {
                "Origin": "https://bailanysta-front.onrender.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            }
            r = client.options("/api/v1/auth/demo", headers=headers)
            assert r.status_code == 200, f"Failed for origins={origins!r}: {r.status_code} {r.text}"
            assert r.headers.get("access-control-allow-origin") == "https://bailanysta-front.onrender.com"
        finally:
            app.dependency_overrides.clear()
            engine.dispose()
    # Restore once after loop
    if orig_cors is not None:
        os.environ["CORS_ORIGINS"] = orig_cors
    else:
        os.environ.pop("CORS_ORIGINS", None)
    if orig_env is not None:
        os.environ["APP_ENV"] = orig_env
    else:
        os.environ.pop("APP_ENV", None)
    if orig_secret is not None:
        os.environ["SECRET_KEY"] = orig_secret
    else:
        os.environ.pop("SECRET_KEY", None)
    import app.core.config
    importlib.reload(app.core.config)
    import app.core.security
    importlib.reload(app.core.security)
    import app.api.v1.auth
    importlib.reload(app.api.v1.auth)
    import app.main
    importlib.reload(app.main)

def test_cors_rejects_unknown_origin():
    orig_cors = os.environ.get("CORS_ORIGINS")
    orig_env = os.environ.get("APP_ENV")
    orig_secret = os.environ.get("SECRET_KEY")
    client, app, engine = _client_with_cors("https://bailanysta-front.onrender.com")
    try:
        headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        r = client.options("/api/v1/auth/demo", headers=headers)
        # Should be 400 for disallowed origin (Starlette returns 400)
        assert r.status_code == 400
        assert "access-control-allow-origin" not in r.headers or r.headers.get("access-control-allow-origin") != "https://evil.com"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        if orig_cors is not None:
            os.environ["CORS_ORIGINS"] = orig_cors
        else:
            os.environ.pop("CORS_ORIGINS", None)
        if orig_env is not None:
            os.environ["APP_ENV"] = orig_env
        else:
            os.environ.pop("APP_ENV", None)
        if orig_secret is not None:
            os.environ["SECRET_KEY"] = orig_secret
        else:
            os.environ.pop("SECRET_KEY", None)
        import app.core.config
        importlib.reload(app.core.config)
        import app.core.security
        importlib.reload(app.core.security)
        import app.api.v1.auth
        importlib.reload(app.api.v1.auth)
        import app.main
        importlib.reload(app.main)

def test_cross_site_auth_cookie_flow():
    # Production cross-site: frontend https://bailanysta-front.onrender.com, backend https://bailanysta-back.onrender.com are cross-site (onrender.com is public suffix)
    # Cookie must be SameSite=None; Secure to be sent with credentials: include
    orig_cors = os.environ.get("CORS_ORIGINS")
    orig_env = os.environ.get("APP_ENV")
    orig_secret = os.environ.get("SECRET_KEY")
    os.environ["CORS_ORIGINS"] = "https://bailanysta-front.onrender.com"
    os.environ["APP_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret-key-1234567890abcdef1234567890abcdef"
    import app.core.config
    importlib.reload(app.core.config)
    import app.core.security
    importlib.reload(app.core.security)
    import app.api.v1.auth
    importlib.reload(app.api.v1.auth)
    import app.main
    importlib.reload(app.main)
    from app.main import app as fastapi_app
    from app.database.session import get_db
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
    # Use https base_url for Secure cookies
    client = TestClient(fastapi_app, base_url="https://testserver")
    try:
        r = client.post("/api/v1/auth/demo", headers={"Origin": "https://bailanysta-front.onrender.com"})
        assert r.status_code == 200
        cookie = r.headers.get("set-cookie", "")
        assert "SameSite=none" in cookie or "SameSite=None" in cookie or "samesite=none" in cookie.lower(), f"Expected SameSite=None, got {cookie}"
        assert "Secure" in cookie, f"Expected Secure, got {cookie}"
        assert "HttpOnly" in cookie
        # Subsequent GET /me with same cross-site Origin should succeed (cookie sent)
        r2 = client.get("/api/v1/auth/me", headers={"Origin": "https://bailanysta-front.onrender.com"})
        assert r2.status_code == 200, f"Expected 200 for /me cross-site, got {r2.status_code} {r2.text}"
        assert r2.json()["username"] == "demo"
    finally:
        fastapi_app.dependency_overrides.clear()
        engine.dispose()
        if orig_cors is not None:
            os.environ["CORS_ORIGINS"] = orig_cors
        else:
            os.environ.pop("CORS_ORIGINS", None)
        if orig_env is not None:
            os.environ["APP_ENV"] = orig_env
        else:
            os.environ.pop("APP_ENV", None)
        if orig_secret is not None:
            os.environ["SECRET_KEY"] = orig_secret
        else:
            os.environ.pop("SECRET_KEY", None)
        import app.core.config
        importlib.reload(app.core.config)
        import app.core.security
        importlib.reload(app.core.security)
        import app.api.v1.auth
        importlib.reload(app.api.v1.auth)
        import app.main
        importlib.reload(app.main)
