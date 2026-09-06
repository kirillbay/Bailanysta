"""Password hashing (Argon2id) + JWT utilities."""

from datetime import datetime, timedelta, timezone
import uuid

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from fastapi import Request

from app.core.config import settings

# Argon2id with default params (time_cost 3, memory 65536, parallelism 4) — safe for MVP
_ph = PasswordHasher()

COOKIE_NAME = "access_token"


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def create_access_token(user_id: uuid.UUID, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    )
    iat = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": iat,
        "type": "access",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


def decode_token(token: str) -> dict:
    """Decode and verify JWT. Raises jwt exceptions on failure."""
    # Explicitly require algorithm, no alg=none
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload


def set_auth_cookie(response, token: str, request: Request | None = None):
    """Set HttpOnly cookie with correct attributes per environment.

    For cross-site production (frontend onrender.com, backend onrender.com are
    cross-site because onrender.com is a public suffix), SameSite=Lax would
    block the cookie on subsequent fetch with credentials: include.
    We use SameSite=None whenever the request is cross-site over HTTPS,
    even if APP_ENV is not strictly 'production' (Render may not have set it).
    """
    max_age = settings.access_token_expire_minutes * 60
    # Determine if we should use SameSite=None:
    # - In production (APP_ENV=production) always use None (cross-site on onrender.com)
    # - Or if the request is HTTPS and Origin is different from Host (cross-site)
    samesite = "lax"
    secure = settings.is_production
    if request is not None:
        # Check if request is cross-site HTTPS
        origin = request.headers.get("origin", "")
        host = request.headers.get("host", "")
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        scheme = request.url.scheme if hasattr(request.url, "scheme") else "http"
        # If behind Render's proxy, X-Forwarded-Proto will be https
        is_https = forwarded_proto == "https" or scheme == "https"
        # If Origin is present and different host, it's cross-site
        if origin and host and origin not in ("", f"https://{host}", f"http://{host}"):
            # For onrender.com public suffix, any two different subdomains are cross-site
            # Use None for cross-site HTTPS
            if is_https or settings.is_production:
                samesite = "none"
                secure = True
        elif settings.is_production:
            # In production, even without Origin (e.g., initial demo POST), use None for safety
            samesite = "none"
            secure = True
    else:
        # Fallback to production check
        if settings.is_production:
            samesite = "none"
            secure = True

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=secure,  # Secure required for SameSite=None
        samesite=samesite,
        path="/",
        max_age=max_age,
    )


def clear_auth_cookie(response, request: Request | None = None):
    samesite = "none" if settings.is_production else "lax"
    secure = settings.is_production
    # Also check request for cross-site to ensure delete matches set
    if request is not None:
        origin = request.headers.get("origin", "")
        host = request.headers.get("host", "")
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        scheme = request.url.scheme if hasattr(request.url, "scheme") else "http"
        is_https = forwarded_proto == "https" or scheme == "https"
        if origin and host and origin not in ("", f"https://{host}", f"http://{host}") and (is_https or settings.is_production):
            samesite = "none"
            secure = True
        elif settings.is_production:
            samesite = "none"
            secure = True
    response.delete_cookie(key=COOKIE_NAME, path="/", secure=secure, samesite=samesite, httponly=True)
