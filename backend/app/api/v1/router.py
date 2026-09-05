from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.posts import router as posts_router
from app.api.v1.feed import router as feed_router
from app.api.v1.comments import router as comments_router
from app.api.v1.bookmarks import router as bookmarks_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(posts_router, tags=["posts"])
api_router.include_router(feed_router, tags=["feed"])
api_router.include_router(comments_router, tags=["comments"])
api_router.include_router(bookmarks_router, tags=["bookmarks"])
