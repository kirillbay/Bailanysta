"""Hashtag endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.post import Hashtag, Post
from app.models.social import PostLike, Comment, PostRepost, Bookmark

router = APIRouter(prefix="/hashtags", tags=["hashtags"])

def _enrich(posts, db):
    if not posts:
        return []
    ids = [p.id for p in posts]
    likes = {r[0]: r[1] for r in db.query(PostLike.post_id, func.count(PostLike.id)).filter(PostLike.post_id.in_(ids)).group_by(PostLike.post_id).all()}
    comments = {r[0]: r[1] for r in db.query(Comment.post_id, func.count(Comment.id)).filter(Comment.post_id.in_(ids)).group_by(Comment.post_id).all()}
    reposts = {r[0]: r[1] for r in db.query(PostRepost.post_id, func.count(PostRepost.id)).filter(PostRepost.post_id.in_(ids)).group_by(PostRepost.post_id).all()}
    result = []
    for p in posts:
        result.append({
            "id": p.id, "author_id": p.author_id, "content": p.content, "created_at": p.created_at, "updated_at": p.updated_at,
            "author": {"id": p.author.id, "username": p.author.username, "display_name": p.author.display_name, "avatar_url": p.author.avatar_url} if p.author else None,
            "media": [{"id": m.id, "url": m.url, "mime_type": m.mime_type, "position": m.position} for m in (p.media or [])],
            "hashtags": [h.name for h in (p.hashtags or [])],
            "likes_count": likes.get(p.id,0), "comments_count": comments.get(p.id,0), "reposts_count": reposts.get(p.id,0),
            "liked_by_me": False, "reposted_by_me": False, "bookmarked_by_me": False,
        })
    return result

@router.get("/{name}")
def get_hashtag(name: str, db: Session = Depends(get_db)):
    n = name.strip().lower().lstrip("#")
    tag = db.query(Hashtag).filter(func.lower(Hashtag.name) == n).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    count = db.query(func.count(Post.id)).join(Post.hashtags).filter(Hashtag.id == tag.id).scalar() or 0
    return {"id": str(tag.id), "name": tag.name, "posts_count": count, "created_at": tag.created_at}

@router.get("/{name}/posts")
def get_hashtag_posts(name: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    n = name.strip().lower().lstrip("#")
    tag = db.query(Hashtag).filter(func.lower(Hashtag.name) == n).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    posts = db.query(Post).join(Post.hashtags).filter(Hashtag.id == tag.id).order_by(Post.created_at.desc()).limit(min(limit,50)).offset(offset).all()
    return _enrich(posts, db)
