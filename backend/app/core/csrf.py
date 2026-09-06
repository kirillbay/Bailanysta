"""CSRF protection for cookie-based auth.

SameSite=Lax is not sufficient for all cross-site scenarios.
We add Origin/Referer validation for state-changing requests when cookies are present.
"""

from fastapi import Request, HTTPException
from urllib.parse import urlparse


def _get_origin(request: Request) -> str | None:
    origin = request.headers.get("origin")
    if origin:
        return origin
    referer = request.headers.get("referer")
    if referer:
        try:
            parsed = urlparse(referer)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            pass
    return None


def check_csrf(request: Request, allowed_origins: list[str]):
    """Raise 403 if CSRF is detected for mutating requests with cookies."""
    method = request.method.upper()
    if method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    # Only check if request carries cookies (i.e., could be cross-site)
    if not request.cookies:
        return
    origin = _get_origin(request)
    # If no Origin/Referer header at all, allow same-site requests (browser may omit for same-site).
    # Only enforce if Origin is present and does not match allowed.
    if origin is None:
        return
    # Normalize allowed origins
    allowed = set(o.strip().rstrip("/") for o in allowed_origins if o.strip())
    # Also allow same host without explicit origin? If origin matches host header, allow.
    host = request.headers.get("host")
    if host and origin.endswith(host):
        return
    if origin.rstrip("/") not in allowed:
        # Check if origin host matches allowed host part loosely (for prod)
        # Parse origin netloc
        try:
            o_parsed = urlparse(origin)
            o_netloc = o_parsed.netloc.lower()
            for a in allowed:
                a_parsed = urlparse(a)
                if a_parsed.netloc.lower() == o_netloc:
                    return
        except Exception:
            pass
        raise HTTPException(status_code=403, detail="CSRF check failed: origin not allowed")
