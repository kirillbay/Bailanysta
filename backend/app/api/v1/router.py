from fastapi import APIRouter
from app.api.v1.health import router as health_router

api_router = APIRouter()

# Health is versioned under /api/v1/health
api_router.include_router(health_router, tags=["health"])
