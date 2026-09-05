"""Posts CRUD + media + hashtags."""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post, PostMedia, Hashtag
from app.schemas.post import PostRead, AuthorPublic, PostMediaRead, PostUpdateInput
from app.services.storage import save_image
from app.services.hashtags import extract_hashtags
from app.core.config import settings

router = APIRouter(prefix="/posts", tags=["posts"])

MAX_MEDIA_PER_POST = 4
MAX_CONTENT_LEN = 10000

def _post_to_read(post: Post) -> dict:
    return {
        "id": post.id,
        "author_id": post.author_id,
        "content": post.content,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "display_name": post.author.display_name,
            "avatar_url": post.author.avatar_url,
        } if post.author else None,
        "media": [{"id": m.id, "url": m.url, "mime_type": m.mime_type, "position": m.position} for m in (post.media or [])],
        "hashtags": [h.name for h in (post.hashtags or [])],
    }

def _handle_hashtags(db: Session, post: Post, content: str):
    names = extract_hashtags(content)
    if not names and not post.hashtags:
        return
    # Clear existing then set new
    post.hashtags.clear()
    for name in names:
        tag = db.query(Hashtag).filter(Hashtag.name == name).first()
        if not tag:
            tag = Hashtag(name=name)
            db.add(tag)
            db.flush()
        post.hashtags.append(tag)

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

    # Validate and save media first (but track for cleanup on DB fail)
    saved_urls: list[str] = []
    saved_paths: list[Path] = []
    media_infos = []
    for idx, f in enumerate(files):
        if not f.filename:
            continue
        data = await f.read()
        if not data:
            continue
        # save_image validates mime, size, Pillow
        try:
            fs_path, public_url = save_image(data, f.content_type, subdir="posts")
        except HTTPException as e:
            # cleanup already saved
            for p in saved_paths:
                try:
                    Path(p).unlink(missing_ok=True)
                except Exception:
                    pass
            raise e
        saved_paths.append(Path(fs_path))
        saved_urls.append(public_url)
        media_infos.append((public_url, f.content_type, idx))

    try:
        post = Post(author_id=current_user.id, content=content)
        db.add(post)
        db.flush()  # get post.id
        for url, mime, pos in media_infos:
            pm = PostMedia(post_id=post.id, url=url, mime_type=mime or "image/jpeg", position=pos)
            db.add(pm)
        _handle_hashtags(db, post, content)
        db.commit()
        db.refresh(post)
        # reload with relationships
        post = db.query(Post).filter(Post.id == post.id).first()
        return _post_to_read(post)
    except Exception as e:
        db.rollback()
        # cleanup files on failure
        for p in saved_paths:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: uuid.UUID, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_to_read(post)

@router.get("/by/user/{username}", response_model=List[PostRead])
def get_user_posts(username: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(limit, 50)
    posts = db.query(Post).filter(Post.author_id == user.id).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return [_post_to_read(p) for p in posts]

# Alternative route for spec GET /users/{username}/posts — we provide redirect-like handler via users router? Instead also support direct
# We'll also add alias in users router, but for now provide this.

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
    return _post_to_read(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    # collect file paths for cleanup
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
