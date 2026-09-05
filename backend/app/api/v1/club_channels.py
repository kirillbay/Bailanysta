"""Club channels API."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.club import Club, ClubMember
from app.models.club_channel import ClubChannel, channel_slugify
from app.schemas.club_channel import ChannelCreate, ChannelUpdate

router = APIRouter(prefix="/clubs", tags=["channels"])

def _member_role(db, club_id, user_id):
    m = db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id).first()
    return m.role if m else None

def _require_member(db, club, user_id):
    role = _member_role(db, club.id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Not a member")
    return role

def _require_admin(db, club, user_id):
    role = _member_role(db, club.id, user_id)
    if role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Admin or owner required")
    return role

def _get_club_or_404(db, slug):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.get("/{slug}/channels")
def list_channels(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    channels = db.query(ClubChannel).filter(ClubChannel.club_id == club.id).order_by(ClubChannel.position.asc(), ClubChannel.created_at.asc()).all()
    return [{"id": c.id, "club_id": c.club_id, "name": c.name, "slug": c.slug, "description": c.description, "position": c.position, "created_at": c.created_at, "updated_at": c.updated_at} for c in channels]

@router.get("/{slug}/channels/{channel_slug}")
def get_channel(slug: str, channel_slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_member(db, club, current_user.id)
    ch = db.query(ClubChannel).filter(ClubChannel.club_id == club.id, ClubChannel.slug == channel_slug.strip()).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"id": ch.id, "club_id": ch.club_id, "name": ch.name, "slug": ch.slug, "description": ch.description, "position": ch.position, "created_at": ch.created_at, "updated_at": ch.updated_at}

@router.post("/{slug}/channels", status_code=status.HTTP_201_CREATED)
def create_channel(slug: str, payload: ChannelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_admin(db, club, current_user.id)
    base_slug = channel_slugify(payload.name)
    ch_slug = base_slug
    counter = 1
    while db.query(ClubChannel).filter(ClubChannel.club_id == club.id, ClubChannel.slug == ch_slug).first():
        ch_slug = f"{base_slug}-{counter}"
        counter += 1
        if counter > 100:
            raise HTTPException(status_code=400, detail="Could not generate slug")
    max_pos = db.query(func.max(ClubChannel.position)).filter(ClubChannel.club_id == club.id).scalar() or 0
    ch = ClubChannel(club_id=club.id, name=payload.name.strip(), slug=ch_slug, description=payload.description.strip() if payload.description else None, position=max_pos + 1)
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return {"id": ch.id, "club_id": ch.club_id, "name": ch.name, "slug": ch.slug, "description": ch.description, "position": ch.position, "created_at": ch.created_at, "updated_at": ch.updated_at}

@router.patch("/{slug}/channels/{channel_slug}")
def update_channel(slug: str, channel_slug: str, payload: ChannelUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_admin(db, club, current_user.id)
    ch = db.query(ClubChannel).filter(ClubChannel.club_id == club.id, ClubChannel.slug == channel_slug.strip()).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    if payload.name is not None:
        ch.name = payload.name.strip()
        # slug not updated for stability (could update but keep simple)
    if payload.description is not None:
        ch.description = payload.description.strip() if payload.description.strip() else None
    db.commit()
    db.refresh(ch)
    return {"id": ch.id, "club_id": ch.club_id, "name": ch.name, "slug": ch.slug, "description": ch.description, "position": ch.position, "created_at": ch.created_at, "updated_at": ch.updated_at}

@router.delete("/{slug}/channels/{channel_slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(slug: str, channel_slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = _get_club_or_404(db, slug)
    _require_admin(db, club, current_user.id)
    ch = db.query(ClubChannel).filter(ClubChannel.club_id == club.id, ClubChannel.slug == channel_slug.strip()).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")
    db.delete(ch)
    db.commit()
    return None
