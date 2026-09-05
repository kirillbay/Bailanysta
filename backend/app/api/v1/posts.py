"""Posts CRUD + media + hashtags + social interactions."""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post, PostMedia, Hashtag
from app.models.social import PostLike, Comment, PostRepost, Bookmark
from app.schemas.post import PostRead, AuthorPublic, PostMediaRead, PostUpdateInput
from app.services.storage import save_image
from app.services.hashtags import extract_hashtags
from app.core.config import settings

router = APIRouter(prefix="/posts", tags=["posts"])

MAX_MEDIA_PER_POST = 4
MAX_CONTENT_LEN = 10000

def _enrich_single(post: Post, db: Session, current_user_id=None):
    if not post:
        return None
    return _enrich_many([post], db, current_user_id)[0]

def _enrich_many(posts: List[Post], db: Session, current_user_id=None):
    if not posts:
        return []
    ids = [p.id for p in posts]
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

def _handle_hashtags(db: Session, post: Post, content: str):
    names = extract_hashtags(content)
    if not names and not post.hashtags:
        return
    post.hashtags.clear()
    for name in names:
        tag = db.query(Hashtag).filter(Hashtag.name == name).first()
        if not tag:
            tag = Hashtag(name=name)
            db.add(tag)
            db.flush()
        post.hashtags.append(tag)

def _get_current_user_optional(request: Request, db: Session):
    from app.core.security import COOKIE_NAME, decode_token
    import jwt, uuid as _uuid
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = decode_token(token)
        uid = _uuid.UUID(str(payload.get("sub")))
        user = db.query(User).filter(User.id == uid).first()
        if user and user.is_active and payload.get("type") == "access":
            return user
    except Exception:
        pass
    return None

@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    content: str = Form(..., min_length=1, max_length=MAX_CONTENT_LEN),
    files: Optional[List[UploadFile]] = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = files or []
    stripped = content.strip()
    if not stripped and not files:
        raise HTTPException(status_code=422, detail="Post must have content or media")
    if len(content) > MAX_CONTENT_LEN:
        raise HTTPException(status_code=422, detail="Content too long")
    if len(files) > MAX_MEDIA_PER_POST:
        raise HTTPException(status_code=422, detail=f"Max {MAX_MEDIA_PER_POST} images per post")

    saved_paths: list[Path] = []
    media_infos = []
    for idx, f in enumerate(files):
        if not f.filename:
            continue
        data = await f.read()
        if not data:
            continue
        try:
            fs_path, public_url = save_image(data, f.content_type, subdir="posts")
        except HTTPException as e:
            for p in saved_paths:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception:
                    pass
            raise e
        saved_paths.append(Path(fs_path))
        media_infos.append((public_url, f.content_type, idx))

    try:
        post = Post(author_id=current_user.id, content=content)
        db.add(post)
        db.flush()
        for url, mime, pos in media_infos:
            pm = PostMedia(post_id=post.id, url=url, mime_type=mime or "image/jpeg", position=pos)
            db.add(pm)
        _handle_hashtags(db, post, content)
        db.commit()
        db.refresh(post)
        post = db.query(Post).filter(Post.id == post.id).first()
        return _enrich_single(post, db, current_user.id)
    except Exception as e:
        db.rollback()
        for p in saved_paths:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = _get_current_user_optional(request, db)
    return _enrich_single(post, db, user.id if user else None)

@router.get("/by/user/{username}", response_model=List[PostRead])
def get_user_posts(username: str, request: Request, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(limit, 50)
    posts = db.query(Post).filter(Post.author_id == user.id).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    current = _get_current_user_optional(request, db)
    return _enrich_many(posts, db, current.id if current else None)

@router.patch("/{post_id}", response_model=PostRead)
def update_post(post_id: uuid.UUID, payload: PostUpdateInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = payload.content
    if not content.strip():
        raise HTTPException(status_code=422, detail="Content cannot be empty")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    post.content = content
    _handle_hashtags(db, post, content)
    db.commit()
    db.refresh(post)
    post = db.query(Post).filter(Post.id == post.id).first()
    return _enrich_single(post, db, current_user.id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    media_urls = [m.url for m in post.media]
    db.delete(post)
    db.commit()
    for url in media_urls:
        try:
            if url.startswith("/uploads/"):
                fs_path = Path(settings.upload_dir) / url.replace("/uploads/", "", 1)
                if fs_path.exists():
                    fs_path.unlink(missing_ok=True)
        except Exception:
            pass
    return None

# ── Likes ──
@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id).first()
    if existing:
        return {"detail": "Already liked"}
    like = PostLike(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    # notification to post author (not self)
    if post.author_id != current_user.id:
        try:
            from app.services.notifications import notify_like
            from app.realtime.manager import manager
            n = notify_like(db, post.author_id, current_user, post.id)
            if n:
                db.commit()
                await manager.send_to_user(str(post.author_id), {"type": "notification.created", "payload": {"id": str(n.id), "type": n.type, "title": n.title, "message": n.message, "actor": {"id": str(current_user.id), "username": current_user.username}, "entity_type": n.entity_type, "entity_id": str(n.entity_id) if n.entity_id else None, "is_read": n.is_read, "created_at": n.created_at.isoformat()}})
        except Exception:
            pass
    return {"detail": "Liked"}

@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    like = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id).first()
    if not like:
        return None
    db.delete(like)
    db.commit()
    return None

# ── Reposts ──
@router.post("/{post_id}/repost", status_code=status.HTTP_201_CREATED)
def repost(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.query(PostRepost).filter(PostRepost.post_id == post_id, PostRepost.user_id == current_user.id).first()
    if existing:
        return {"detail": "Already reposted"}
    rp = PostRepost(post_id=post_id, user_id=current_user.id)
    db.add(rp)
    db.commit()
    return {"detail": "Reposted"}

@router.delete("/{post_id}/repost", status_code=status.HTTP_204_NO_CONTENT)
def unrepost(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    rp = db.query(PostRepost).filter(PostRepost.post_id == post_id, PostRepost.user_id == current_user.id).first()
    if not rp:
        return None
    db.delete(rp)
    db.commit()
    return None

# ── Bookmarks ──
@router.post("/{post_id}/bookmark", status_code=status.HTTP_201_CREATED)
def bookmark(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.query(Bookmark).filter(Bookmark.post_id == post_id, Bookmark.user_id == current_user.id).first()
    if existing:
        return {"detail": "Already bookmarked"}
    bm = Bookmark(post_id=post_id, user_id=current_user.id)
    db.add(bm)
    db.commit()
    return {"detail": "Bookmarked"}

@router.delete("/{post_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def unbookmark(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    bm = db.query(Bookmark).filter(Bookmark.post_id == post_id, Bookmark.user_id == current_user.id).first()
    if not bm:
        return None
    db.delete(bm)
    db.commit()
    return None
