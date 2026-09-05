"""Follow endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.follow import Follow

router = APIRouter(prefix="/users", tags=["follows"])

def _enrich_user(u: User, db: Session, current_user_id=None):
    followers = db.query(func.count(Follow.id)).filter(Follow.following_id == u.id).scalar() or 0
    following = db.query(func.count(Follow.id)).filter(Follow.follower_id == u.id).scalar() or 0
    is_following = False
    if current_user_id:
        is_following = db.query(Follow).filter(Follow.follower_id == current_user_id, Follow.following_id == u.id).first() is not None
    return {
        "id": u.id, "username": u.username, "display_name": u.display_name, "bio": u.bio, "avatar_url": u.avatar_url, "cover_url": u.cover_url, "created_at": u.created_at,
        "followers_count": followers, "following_count": following, "is_following": is_following
    }

@router.post("/{username}/follow", status_code=status.HTTP_201_CREATED)
def follow_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target = db.query(User).filter(User.username == username.strip()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    existing = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.following_id == target.id).first()
    if existing:
        return {"detail": "Already following"}
    f = Follow(follower_id=current_user.id, following_id=target.id)
    db.add(f)
    db.commit()
    return {"detail": "Followed"}

@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target = db.query(User).filter(User.username == username.strip()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    f = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.following_id == target.id).first()
    if not f:
        return None
    db.delete(f)
    db.commit()
    return None

@router.get("/{username}/followers")
def followers(username: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    target = db.query(User).filter(User.username == username.strip()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # optional auth for is_following
    from fastapi import Request
    # we don't have request here, so without is_following
    q = db.query(User).join(Follow, Follow.follower_id == User.id).filter(Follow.following_id == target.id).order_by(Follow.created_at.desc())
    total = q.count()
    users = q.offset(offset).limit(min(limit,50)).all()
    items = []
    for u in users:
        followers = db.query(func.count(Follow.id)).filter(Follow.following_id == u.id).scalar() or 0
        following = db.query(func.count(Follow.id)).filter(Follow.follower_id == u.id).scalar() or 0
        items.append({"id": u.id, "username": u.username, "display_name": u.display_name, "bio": u.bio, "avatar_url": u.avatar_url, "created_at": u.created_at, "followers_count": followers, "following_count": following})
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/{username}/following")
def following(username: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    target = db.query(User).filter(User.username == username.strip()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    q = db.query(User).join(Follow, Follow.following_id == User.id).filter(Follow.follower_id == target.id).order_by(Follow.created_at.desc())
    total = q.count()
    users = q.offset(offset).limit(min(limit,50)).all()
    items = []
    for u in users:
        followers = db.query(func.count(Follow.id)).filter(Follow.following_id == u.id).scalar() or 0
        following_ct = db.query(func.count(Follow.id)).filter(Follow.follower_id == u.id).scalar() or 0
        items.append({"id": u.id, "username": u.username, "display_name": u.display_name, "bio": u.bio, "avatar_url": u.avatar_url, "created_at": u.created_at, "followers_count": followers, "following_count": following_ct})
    return {"items": items, "total": total, "limit": limit, "offset": offset}
