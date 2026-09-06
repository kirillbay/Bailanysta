"""Unified search."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import sqlalchemy as sa
from sqlalchemy import func, or_

from app.database.session import get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.models.post import Post, Hashtag
from app.models.follow import Follow
from app.models.social import PostLike, Comment, PostRepost, Bookmark
from app.models.project import Project

router = APIRouter(prefix="/search", tags=["search"])

MAX_Q_LEN = 100

def _escape_like(s: str) -> str:
    # Escape SQL wildcards for LIKE
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def _post_enrich(posts, db, q_user_id=None):
    if not posts:
        return []
    ids = [p.id for p in posts]
    likes = {r[0]: r[1] for r in db.query(PostLike.post_id, func.count(PostLike.id)).filter(PostLike.post_id.in_(ids)).group_by(PostLike.post_id).all()}
    comments = {r[0]: r[1] for r in db.query(Comment.post_id, func.count(Comment.id)).filter(Comment.post_id.in_(ids)).group_by(Comment.post_id).all()}
    reposts = {r[0]: r[1] for r in db.query(PostRepost.post_id, func.count(PostRepost.id)).filter(PostRepost.post_id.in_(ids)).group_by(PostRepost.post_id).all()}
    liked = set()
    reposted = set()
    bookmarked = set()
    if q_user_id:
        liked = set(r[0] for r in db.query(PostLike.post_id).filter(PostLike.user_id == q_user_id, PostLike.post_id.in_(ids)).all())
        reposted = set(r[0] for r in db.query(PostRepost.post_id).filter(PostRepost.user_id == q_user_id, PostRepost.post_id.in_(ids)).all())
        bookmarked = set(r[0] for r in db.query(Bookmark.post_id).filter(Bookmark.user_id == q_user_id, Bookmark.post_id.in_(ids)).all())
    result = []
    for p in posts:
        result.append({
            "id": p.id, "author_id": p.author_id, "content": p.content, "created_at": p.created_at, "updated_at": p.updated_at,
            "author": {"id": p.author.id, "username": p.author.username, "display_name": p.author.display_name, "avatar_url": p.author.avatar_url} if p.author else None,
            "media": [{"id": m.id, "url": m.url, "mime_type": m.mime_type, "position": m.position} for m in (p.media or [])],
            "hashtags": [h.name for h in (p.hashtags or [])],
            "likes_count": likes.get(p.id,0), "comments_count": comments.get(p.id,0), "reposts_count": reposts.get(p.id,0),
            "liked_by_me": p.id in liked, "reposted_by_me": p.id in reposted, "bookmarked_by_me": p.id in bookmarked,
        })
    return result

@router.get("", response_model=dict)
def search(q: str = Query("", max_length=MAX_Q_LEN), type: str = Query("all", pattern="^(all|users|posts|hashtags|projects)$"), limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0), db: Session = Depends(get_db), _rl: bool = Depends(rate_limit(limit=30, window=60, key_prefix="search"))):
    q = (q or "").strip()
    if not q:
        return {"users": [], "posts": [], "hashtags": [], "projects": [], "query": q}
    if len(q) > MAX_Q_LEN:
        raise HTTPException(status_code=422, detail="Query too long")
    # optional current user for is_following/liked flags — try to get from cookie but search is public, so no auth required
    result = {"query": q, "users": [], "posts": [], "hashtags": [], "projects": []}
    q_lower = _escape_like(q.lower().lstrip("#"))
    # Users
    if type in ("all", "users"):
        like = f"%{q_lower}%"
        users = db.query(User).filter(or_(func.lower(User.username).like(like, escape="\\"), func.lower(User.display_name).like(like, escape="\\"))).limit(min(limit,50)).offset(offset).all()
        enriched = []
        for u in users:
            followers = db.query(func.count(Follow.id)).filter(Follow.following_id == u.id).scalar() or 0
            following = db.query(func.count(Follow.id)).filter(Follow.follower_id == u.id).scalar() or 0
            enriched.append({"id": u.id, "username": u.username, "display_name": u.display_name, "bio": u.bio, "avatar_url": u.avatar_url, "created_at": u.created_at, "followers_count": followers, "following_count": following})
        result["users"] = enriched
    # Posts
    if type in ("all", "posts"):
        # content ILIKE or hashtag
        like = f"%{q_lower}%"
        posts = db.query(Post).filter(func.lower(Post.content).like(like, escape="\\")).order_by(Post.created_at.desc()).limit(min(limit,50)).offset(offset).all()
        result["posts"] = _post_enrich(posts, db)
    # Hashtags
    if type in ("all", "hashtags"):
        like = f"%{q_lower}%"
        tags = db.query(Hashtag).filter(func.lower(Hashtag.name).like(like, escape="\\")).limit(min(limit,50)).offset(offset).all()
        # count posts per hashtag
        result["hashtags"] = [{"id": str(t.id), "name": t.name, "posts_count": db.query(func.count(Post.id)).join(Post.hashtags).filter(Hashtag.id == t.id).scalar() or 0} for t in tags]
    # Projects — search by name / description / technologies (ILIKE for MVP, parameterized)
    if type in ("all", "projects"):
        like = f"%{q_lower}%"
        # technologies is JSON; for SQLite json column is text, cast to string
        # Use func.lower on casted fields where applicable
        projects = db.query(Project).filter(
            or_(
                func.lower(Project.name).like(like, escape="\\"),
                func.lower(Project.description).like(like, escape="\\"),
                func.lower(func.cast(Project.technologies, sa.String)).like(like, escape="\\"),
            )
        ).order_by(Project.created_at.desc()).limit(min(limit,50)).offset(offset).all()
        result["projects"] = [
            {
                "id": str(p.id),
                "owner_id": str(p.owner_id),
                "name": p.name,
                "description": p.description[:200],
                "technologies": p.technologies or [],
                "github_url": p.github_url,
                "demo_url": p.demo_url,
                "image_url": p.image_url,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    return result
