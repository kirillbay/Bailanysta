"""Notifications API."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

def _to_read(n: Notification, db: Session):
    actor = None
    if n.actor_id:
        actor = db.query(User).filter(User.id == n.actor_id).first()
    return {
        "id": n.id, "recipient_id": n.recipient_id, "actor_id": n.actor_id,
        "actor": {"id": actor.id, "username": actor.username, "display_name": actor.display_name, "avatar_url": actor.avatar_url} if actor else None,
        "type": n.type, "title": n.title, "message": n.message, "entity_type": n.entity_type, "entity_id": n.entity_id,
        "is_read": n.is_read, "created_at": n.created_at
    }

@router.get("", response_model=list)
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), unread_only: bool = Query(False)):
    q = db.query(Notification).filter(Notification.recipient_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc())
    notifs = q.offset(offset).limit(min(limit,100)).all()
    return [_to_read(n, db) for n in notifs]

@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cnt = db.query(func.count(Notification.id)).filter(Notification.recipient_id == current_user.id, Notification.is_read == False).scalar() or 0
    return {"count": cnt}

@router.patch("/{notification_id}/read")
def mark_read(notification_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    if n.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    n.is_read = True
    db.commit()
    return _to_read(n, db)

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.recipient_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"detail": "All marked as read"}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    if n.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    db.delete(n)
    db.commit()
    return None
