"""Club channel messages."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.club import Club, ClubMember
from app.models.club_channel import ClubChannel
from app.models.club_message import ClubMessage
from app.schemas.club_channel import MessageCreate, MessageUpdate

router = APIRouter(prefix="/clubs", tags=["messages"])

def _get_club_or_404(db, slug):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

def _get_channel_or_404(db, club, channel_slug):
    ch = db.query(ClubChannel).filter(ClubChannel.club_id == club.id, ClubChannel.slug == channel_slug.strip()).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ch

def _require_member(db, club, user_id):
    m = db.query(ClubMember).filter(ClubMember.club_id == club.id, ClubMember.user_id == user_id).first()
    if not m:
        raise HTTPException(status_code=403, detail="Not a member")
    return m

def _can_delete_other(db, club, user_id):
    m = db.query(ClubMember).filter(ClubMember.club_id == club.id, ClubMember.user_id == user_id).first()
    if not m:
        return False
    return m.role in ("owner", "admin", "moderator")

def _msg_to_read(m: ClubMessage):
    return {
        "id": m.id, "channel_id": m.channel_id, "author_id": m.author_id, "content": m.content, "is_edited": m.is_edited,
        "created_at": m.created_at, "updated_at": m.updated_at,
        "author": {"id": m.author.id, "username": m.author.username, "display_name": m.author.display_name, "avatar_url": m.author.avatar_url} if m.author else None
    }

@router.get("/{slug}/channels/{channel_slug}/messages")
def list_messages(slug: str, channel_slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    ch = _get_channel_or_404(db, club, channel_slug)
    # ensure channel belongs to club (already by query)
    msgs = db.query(ClubMessage).filter(ClubMessage.channel_id == ch.id).order_by(ClubMessage.created_at.asc()).offset(offset).limit(min(limit,100)).all()
    return [_msg_to_read(m) for m in msgs]

@router.post("/{slug}/channels/{channel_slug}/messages", status_code=status.HTTP_201_CREATED)
async def create_message(slug: str, channel_slug: str, payload: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    ch = _get_channel_or_404(db, club, channel_slug)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Content cannot be empty")
    if len(content) > 10000:
        raise HTTPException(status_code=422, detail="Too long")
    msg = ClubMessage(channel_id=ch.id, author_id=current_user.id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    msg = db.query(ClubMessage).filter(ClubMessage.id == msg.id).first()
    data = _msg_to_read(msg)
    # broadcast after commit (ghost-free)
    try:
        from app.realtime.manager import manager
        await manager.broadcast_channel(str(ch.id), {"type": "message.created", "payload": data})
    except Exception:
        pass
    return data

@router.patch("/{slug}/channels/{channel_slug}/messages/{message_id}")
async def update_message(slug: str, channel_slug: str, message_id: uuid.UUID, payload: MessageUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    ch = _get_channel_or_404(db, club, channel_slug)
    msg = db.query(ClubMessage).filter(ClubMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.channel_id != ch.id:
        raise HTTPException(status_code=404, detail="Message not found in this channel")
    if msg.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Content cannot be empty")
    msg.content = content
    msg.is_edited = True
    db.commit()
    db.refresh(msg)
    data = _msg_to_read(msg)
    try:
        from app.realtime.manager import manager
        await manager.broadcast_channel(str(ch.id), {"type": "message.updated", "payload": data})
    except Exception:
        pass
    return data

@router.delete("/{slug}/channels/{channel_slug}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(slug: str, channel_slug: str, message_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    ch = _get_channel_or_404(db, club, channel_slug)
    msg = db.query(ClubMessage).filter(ClubMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.channel_id != ch.id:
        raise HTTPException(status_code=404, detail="Message not found in this channel")
    if msg.author_id != current_user.id and not _can_delete_other(db, club, current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(msg)
    db.commit()
    try:
        from app.realtime.manager import manager
        await manager.broadcast_channel(str(ch.id), {"type": "message.deleted", "payload": {"id": str(message_id), "channel_id": str(ch.id)}})
    except Exception:
        pass
    return None
