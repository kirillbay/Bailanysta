"""Global feed."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post
from app.models.social import PostLike, Comment, PostRepost, Bookmark

router = APIRouter(prefix="/feed", tags=["feed"])

def _enrich(posts, db: Session, current_user_id):
    if not posts:
        return []
    ids = [p.id for p in posts]
    # counts bulk
    likes = {r[0]: r[1] for r in db.query(PostLike.post_id, func.count(PostLike.id)).filter(PostLike.post_id.in_(ids)).group_by(PostLike.post_id).all()}
    comments = {r[0]: r[1] for r in db.query(Comment.post_id, func.count(Comment.id)).filter(Comment.post_id.in_(ids)).group_by(Comment.post_id).all()}
    reposts = {r[0]: r[1] for r in db.query(PostRepost.post_id, func.count(PostRepost.id)).filter(PostRepost.post_id.in_(ids)).group_by(PostRepost.post_id).all()}
    liked = set(r[0] for r in db.query(PostLike.post_id).filter(PostLike.user_id == current_user_id, PostLike.post_id.in_(ids)).all()) if current_user_id else set()
    reposted = set(r[0] for r in db.query(PostRepost.post_id).filter(PostRepost.user_id == current_user_id, PostRepost.post_id.in_(ids)).all()) if current_user_id else set()
    bookmarked = set(r[0] for r in db.query(Bookmark.post_id).filter(Bookmark.user_id == current_user_id, Bookmark.post_id.in_(ids)).all()) if current_user_id else set()
    result = []
    for p in posts:
        result.append({
            "id": p.id,
            "author_id": p.author_id,
            "content": p.content,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "author": {"id": p.author.id, "username": p.author.username, "display_name": p.author.display_name, "avatar_url": p.author.avatar_url} if p.author else None,
            "media": [{"id": m.id, "url": m.url, "mime_type": m.mime_type, "position": m.position} for m in (p.media or [])],
            "hashtags": [h.name for h in (p.hashtags or [])],
            "likes_count": likes.get(p.id, 0),
            "comments_count": comments.get(p.id, 0),
            "reposts_count": reposts.get(p.id, 0),
            "liked_by_me": p.id in liked,
            "reposted_by_me": p.id in reposted,
            "bookmarked_by_me": p.id in bookmarked,
        })
    return result

@router.get("", response_model=list)
def global_feed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    # Performance: eager load author/media/hashtags to avoid N+1, bulk counts via _enrich
    posts = db.query(Post).options(selectinload(Post.author), selectinload(Post.media), selectinload(Post.hashtags)).order_by(Post.created_at.desc()).offset(offset).limit(min(limit, 50)).all()
    return _enrich(posts, db, current_user.id)
