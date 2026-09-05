"""Profiles: public GET, own GET/PATCH, avatar/cover upload + user posts."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserPublic, UserRead, UserUpdate
from app.services.storage import save_image

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only owner — current_user is owner, no IDOR
    if payload.display_name is not None:
        current_user.display_name = payload.display_name.strip() if payload.display_name.strip() else None
    if payload.bio is not None:
        current_user.bio = payload.bio.strip() if payload.bio.strip() else None
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{username}/posts")
def get_user_posts(username: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    from fastapi import Request
    from sqlalchemy import func
    from app.models.social import PostLike, Comment, PostRepost, Bookmark

    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(limit, 50)
    posts = db.query(Post).filter(Post.author_id == user.id).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
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
            "likes_count": likes.get(p.id, 0), "comments_count": comments.get(p.id, 0), "reposts_count": reposts.get(p.id, 0),
            "liked_by_me": False, "reposted_by_me": False, "bookmarked_by_me": False,
        })
    return result


@router.get("/{username}")
def get_public_profile(username: str, request: Request, db: Session = Depends(get_db)):
    from sqlalchemy import func
    from app.models.follow import Follow
    from app.core.security import COOKIE_NAME, decode_token
    import uuid as _uuid, jwt

    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    followers = db.query(func.count(Follow.id)).filter(Follow.following_id == user.id).scalar() or 0
    following = db.query(func.count(Follow.id)).filter(Follow.follower_id == user.id).scalar() or 0
    is_following = False
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            payload = decode_token(token)
            uid = _uuid.UUID(str(payload.get("sub")))
            is_following = db.query(Follow).filter(Follow.follower_id == uid, Follow.following_id == user.id).first() is not None
        except Exception:
            pass
    return {
        "id": user.id, "username": user.username, "display_name": user.display_name, "bio": user.bio,
        "avatar_url": user.avatar_url, "cover_url": user.cover_url, "created_at": user.created_at,
        "followers_count": followers, "following_count": following, "is_following": is_following
    }


@router.post("/me/avatar", response_model=UserRead)
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    _, public_url = save_image(data, file.content_type, subdir="avatars")
    current_user.avatar_url = public_url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/cover", response_model=UserRead)
async def upload_cover(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    _, public_url = save_image(data, file.content_type, subdir="covers")
    current_user.cover_url = public_url
    db.commit()
    db.refresh(current_user)
    return current_user
