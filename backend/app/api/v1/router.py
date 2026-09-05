from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.posts import router as posts_router
from app.api.v1.feed import router as feed_router
from app.api.v1.comments import router as comments_router
from app.api.v1.bookmarks import router as bookmarks_router
from app.api.v1.follows import router as follows_router
from app.api.v1.search import router as search_router
from app.api.v1.hashtags import router as hashtags_router
from app.api.v1.stories import router as stories_router
from app.api.v1.clubs import router as clubs_router
from app.api.v1.club_channels import router as channels_router
from app.api.v1.club_messages import router as club_messages_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.realtime import router as realtime_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(posts_router, tags=["posts"])
api_router.include_router(feed_router, tags=["feed"])
api_router.include_router(comments_router, tags=["comments"])
api_router.include_router(bookmarks_router, tags=["bookmarks"])
api_router.include_router(follows_router, tags=["follows"])
api_router.include_router(search_router, tags=["search"])
api_router.include_router(hashtags_router, tags=["hashtags"])
api_router.include_router(stories_router, tags=["stories"])
api_router.include_router(clubs_router, tags=["clubs"])
api_router.include_router(channels_router, tags=["channels"])
api_router.include_router(club_messages_router, tags=["club-messages"])
api_router.include_router(notifications_router, tags=["notifications"])
api_router.include_router(realtime_router, tags=["realtime"])
