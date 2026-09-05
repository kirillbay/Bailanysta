from fastapi import APIRouter
from app.core.config import settings
from app.database.session import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
        "env": settings.app_env,
    }


@router.get("/health/db")
async def health_db():
    """Database connectivity probe — no stack trace on failure."""
    try:
        ok = check_db_connection()
        if ok:
            return {"status": "ok", "database": "connected"}
        return {"status": "error", "database": "unreachable"}
    except Exception:
        # Never leak internals
        return {"status": "error", "database": "unreachable"}
