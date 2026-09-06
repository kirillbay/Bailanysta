"""In-memory rate limiter — single-instance MVP.

Single-instance, no Redis. Suitable for MVP, documented debt for distributed.
Uses sliding window per key (IP or user).
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque

from fastapi import Request, HTTPException

# store: key -> deque of timestamps
_store: Dict[str, Deque[float]] = defaultdict(deque)
# Simple lock not needed for CPython GIL, but keep logic simple


def _get_client_ip(request: Request) -> str:
    # Prefer X-Forwarded-For if behind proxy, else direct
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _is_allowed(key: str, limit: int, window: int) -> bool:
    now = time.time()
    dq = _store[key]
    # evict outside window
    while dq and dq[0] <= now - window:
        dq.popleft()
    # Prune store if too large (prevent memory growth)
    if len(_store) > 5000:
        # Remove empty or oldest keys
        to_del = []
        for k, v in _store.items():
            if not v or (v and v[0] <= now - 3600):
                to_del.append(k)
            if len(to_del) > 1000:
                break
        for k in to_del:
            _store.pop(k, None)
        # If still large, drop oldest key
        if len(_store) > 5000:
            oldest = next(iter(_store))
            _store.pop(oldest, None)
    if len(dq) >= limit:
        return False
    dq.append(now)
    return True


def rate_limit(limit: int, window: int = 60, key_prefix: str = "global", by_user: bool = False):
    """Dependency factory for rate limiting.

    by_user=True uses authenticated user id if available, else IP.
    """
    def dependency(request: Request):
        ip = _get_client_ip(request)
        # Try user prefix if by_user and cookie present (best-effort)
        key = f"{key_prefix}:{ip}"
        if by_user:
            # Attempt to extract user from cookie without full decode (avoid circular import)
            # Fallback to IP if not authenticated
            try:
                from app.core.security import COOKIE_NAME, decode_token
                token = request.cookies.get(COOKIE_NAME)
                if token:
                    payload = decode_token(token)
                    uid = payload.get("sub")
                    if uid:
                        key = f"{key_prefix}:user:{uid}"
            except Exception:
                pass
        if not _is_allowed(key, limit, window):
            raise HTTPException(status_code=429, detail="Too many requests, please try again later")
        return True
    return dependency


def clear_store():
    """For tests — clear all buckets."""
    _store.clear()
