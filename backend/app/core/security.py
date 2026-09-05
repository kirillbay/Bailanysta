"""Password hashing (Argon2id) + JWT utilities."""

from datetime import datetime, timedelta, timezone
import uuid

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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


def set_auth_cookie(response, token: str):
    """Set HttpOnly cookie with correct attributes per environment."""
    # Max age in seconds
    max_age = settings.access_token_expire_minutes * 60
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,  # Secure only in production (HTTPS)
        samesite="lax",  # Lax balances CSRF and usability; strict would break some flows
        path="/",
        max_age=max_age,
    )


def clear_auth_cookie(response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
