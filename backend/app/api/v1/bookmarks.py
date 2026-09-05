"""Bookmarks."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post
from app.models.social import Bookmark, PostLike, Comment, PostRepost

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

def _enrich(posts, db, current_user_id):
    if not posts:
        return []
    ids = [p.id for p in posts]
    likes = {r[0]: r[1] for r in db.query(PostLike.post_id, func.count(PostLike.id)).filter(PostLike.post_id.in_(ids)).group_by(PostLike.post_id).all()}
    comments = {r[0]: r[1] for r in db.query(Comment.post_id, func.count(Comment.id)).filter(Comment.post_id.in_(ids)).group_by(Comment.post_id).all()}
    reposts = {r[0]: r[1] for r in db.query(PostRepost.post_id, func.count(PostRepost.id)).filter(PostRepost.post_id.in_(ids)).group_by(PostRepost.post_id).all()}
    liked = set(r[0] for r in db.query(PostLike.post_id).filter(PostLike.user_id == current_user_id, PostLike.post_id.in_(ids)).all())
    reposted = set(r[0] for r in db.query(PostRepost.post_id).filter(PostRepost.user_id == current_user_id, PostRepost.post_id.in_(ids)).all())
    bookmarked = set(r[0] for r in db.query(Bookmark.post_id).filter(Bookmark.user_id == current_user_id, Bookmark.post_id.in_(ids)).all())
    result = []
    for p in posts:
        result.append({
            "id": p.id, "author_id": p.author_id, "content": p.content, "created_at": p.created_at, "updated_at": p.updated_at,
            "author": {"id": p.author.id, "username": p.author.username, "display_name": p.author.display_name, "avatar_url": p.author.avatar_url} if p.author else None,
            "media": [{"id": m.id, "url": m.url, "mime_type": m.mime_type, "position": m.position} for m in (p.media or [])],
            "hashtags": [h.name for h in (p.hashtags or [])],
            "likes_count": likes.get(p.id, 0), "comments_count": comments.get(p.id, 0), "reposts_count": reposts.get(p.id, 0),
            "liked_by_me": p.id in liked, "reposted_by_me": p.id in reposted, "bookmarked_by_me": p.id in bookmarked,
        })
    return result

@router.get("", response_model=list)
def list_bookmarks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    # Get bookmarked post ids for current user, ordered by bookmark created_at desc
    bms = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).order_by(Bookmark.created_at.desc()).offset(offset).limit(min(limit,50)).all()
    post_ids = [b.post_id for b in bms]
    if not post_ids:
        return []
    # Preserve order as per bookmark order
    posts = db.query(Post).filter(Post.id.in_(post_ids)).all()
    # Map by id
    post_map = {p.id: p for p in posts}
    ordered = [post_map[pid] for pid in post_ids if pid in post_map]
    return _enrich(ordered, db, current_user.id)
