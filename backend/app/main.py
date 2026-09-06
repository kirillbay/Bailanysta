from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.csrf import check_csrf

app = FastAPI(
    title=settings.app_name,
    description="Bailanysta — Social platform for IT communities",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── CSRF protection (Origin check for cookie-based mutating requests) ──
@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    try:
        check_csrf(request, settings.cors_origins_list)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    return await call_next(request)


# ── Security headers ──
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Early body size guard: reject huge content-length before reading
    clen = request.headers.get("content-length")
    if clen:
        try:
            if int(clen) > 10 * 1024 * 1024:  # 10 MB hard cap
                return JSONResponse(status_code=413, content={"detail": "Payload too large"})
        except ValueError:
            pass
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "0"  # modern browsers ignore, CSP is preferred
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # CSP: allow self, inline styles (Tailwind), backend static
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none'"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response


# ── Global error handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Preserve FastAPI HTTPException handling (don't mask 422/401 etc)
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    # Never leak stack trace/SQL internals to client — log internally if needed
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Static uploads (safe, no code execution) ──
upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# ── Routers ──
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Also expose health at root for load balancers / simple checks
@app.get("/health", tags=["health"], include_in_schema=False)
async def root_health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
