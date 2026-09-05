"""Clubs API."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.club import Club, ClubMember, slugify
from app.schemas.club import ClubCreate, ClubUpdate
from app.services.storage import save_image

router = APIRouter(prefix="/clubs", tags=["clubs"])

ROLES = ["owner", "admin", "moderator", "member"]
ROLE_RANK = {"member": 1, "moderator": 2, "admin": 3, "owner": 4}

def _get_member(db: Session, club_id, user_id):
    return db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id).first()

def _member_role(db, club_id, user_id):
    m = _get_member(db, club_id, user_id)
    return m.role if m else None

def _can_edit(db, club, user_id):
    role = _member_role(db, club.id, user_id)
    return role in ("owner", "admin")

def _is_owner(db, club, user_id):
    role = _member_role(db, club.id, user_id)
    return role == "owner"

def _club_to_read(club: Club, db: Session, current_user_id=None):
    count = db.query(func.count(ClubMember.id)).filter(ClubMember.club_id == club.id).scalar() or 0
    is_member = False
    role = None
    if current_user_id:
        m = _get_member(db, club.id, current_user_id)
        if m:
            is_member = True
            role = m.role
    return {
        "id": club.id, "owner_id": club.owner_id, "name": club.name, "slug": club.slug, "description": club.description,
        "avatar_url": club.avatar_url, "cover_url": club.cover_url, "created_at": club.created_at, "updated_at": club.updated_at,
        "members_count": count, "is_member": is_member, "role": role
    }

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_club(payload: ClubCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    base_slug = slugify(payload.name)
    slug = base_slug
    # ensure unique slug
    counter = 1
    while db.query(Club).filter(Club.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
        if counter > 100:
            raise HTTPException(status_code=400, detail="Could not generate slug")
    club = Club(owner_id=current_user.id, name=payload.name.strip(), slug=slug, description=payload.description.strip() if payload.description else None)
    db.add(club)
    db.flush()
    member = ClubMember(club_id=club.id, user_id=current_user.id, role="owner")
    db.add(member)
    db.commit()
    db.refresh(club)
    return _club_to_read(club, db, current_user.id)

@router.get("", response_model=list)
def list_clubs(q: str = Query(default=None, max_length=100), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = db.query(Club)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(or_(func.lower(Club.name).like(like), func.lower(Club.slug).like(like), func.lower(Club.description).like(like)))
    clubs = query.order_by(Club.created_at.desc()).offset(offset).limit(min(limit,50)).all()
    # for public, no current user, counts still
    result = []
    for c in clubs:
        count = db.query(func.count(ClubMember.id)).filter(ClubMember.club_id == c.id).scalar() or 0
        result.append({"id": c.id, "owner_id": c.owner_id, "name": c.name, "slug": c.slug, "description": c.description, "avatar_url": c.avatar_url, "cover_url": c.cover_url, "created_at": c.created_at, "updated_at": c.updated_at, "members_count": count, "is_member": False, "role": None})
    return result

@router.get("/{slug}")
def get_club(slug: str, request: Request, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    count = db.query(func.count(ClubMember.id)).filter(ClubMember.club_id == club.id).scalar() or 0
    # try optional auth for is_member
    is_member = False
    role = None
    try:
        from app.core.security import COOKIE_NAME, decode_token
        import uuid as _uuid
        token = request.cookies.get(COOKIE_NAME)
        if token:
            payload = decode_token(token)
            uid = _uuid.UUID(str(payload.get("sub")))
            m = _get_member(db, club.id, uid)
            if m:
                is_member = True
                role = m.role
    except Exception:
        pass
    return {"id": club.id, "owner_id": club.owner_id, "name": club.name, "slug": club.slug, "description": club.description, "avatar_url": club.avatar_url, "cover_url": club.cover_url, "created_at": club.created_at, "updated_at": club.updated_at, "members_count": count, "is_member": is_member, "role": role}

@router.patch("/{slug}", response_model=dict)
def update_club(slug: str, payload: ClubUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    if not _can_edit(db, club, current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    if payload.name is not None:
        club.name = payload.name.strip()
        # slug not updated on name change for stability
    if payload.description is not None:
        club.description = payload.description.strip() if payload.description.strip() else None
    db.commit()
    db.refresh(club)
    return _club_to_read(club, db, current_user.id)

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    if not _is_owner(db, club, current_user.id):
        raise HTTPException(status_code=403, detail="Only owner can delete")
    db.delete(club)
    db.commit()
    return None

@router.post("/{slug}/join", status_code=status.HTTP_201_CREATED)
def join_club(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    existing = _get_member(db, club.id, current_user.id)
    if existing:
        return {"detail": "Already member"}
    m = ClubMember(club_id=club.id, user_id=current_user.id, role="member")
    db.add(m)
    db.commit()
    return {"detail": "Joined"}

@router.delete("/{slug}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_club(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    member = _get_member(db, club.id, current_user.id)
    if not member:
        return None
    if member.role == "owner":
        raise HTTPException(status_code=400, detail="Owner cannot leave without transfer")
    db.delete(member)
    db.commit()
    return None

@router.get("/{slug}/members")
def list_members(slug: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    q = db.query(ClubMember, User).join(User, ClubMember.user_id == User.id).filter(ClubMember.club_id == club.id).order_by(ClubMember.joined_at.asc())
    total = q.count()
    rows = q.offset(offset).limit(min(limit,50)).all()
    items = []
    for member, user in rows:
        items.append({"id": member.id, "user_id": user.id, "username": user.username, "display_name": user.display_name, "avatar_url": user.avatar_url, "role": member.role, "joined_at": member.joined_at})
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.patch("/{slug}/members/{username}/role")
def update_member_role(slug: str, username: str, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    acting_role = _member_role(db, club.id, current_user.id)
    if acting_role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Not allowed")
    target_user = db.query(User).filter(User.username == username.strip()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    target_member = _get_member(db, club.id, target_user.id)
    if not target_member:
        raise HTTPException(status_code=404, detail="Not a member")
    new_role = payload.get("role")
    if new_role not in ["admin", "moderator", "member"]:
        raise HTTPException(status_code=422, detail="Invalid role (admin/moderator/member only, owner cannot be assigned)")
    if new_role == "owner":
        raise HTTPException(status_code=403, detail="Cannot assign owner via this endpoint")
    if target_member.role == "owner":
        raise HTTPException(status_code=403, detail="Cannot modify owner")
    # Permission matrix
    if acting_role == "admin":
        if target_member.role == "admin":
            raise HTTPException(status_code=403, detail="Admin cannot modify another admin")
        if new_role == "admin":
            raise HTTPException(status_code=403, detail="Admin cannot assign admin")
    if acting_role == "admin" and new_role not in ["moderator", "member"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    # moderator cannot change roles (already blocked by acting_role check)
    target_member.role = new_role
    db.commit()
    return {"detail": f"Role updated to {new_role}"}

@router.delete("/{slug}/members/{username}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(slug: str, username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    acting_role = _member_role(db, club.id, current_user.id)
    if acting_role not in ("owner", "admin", "moderator"):
        raise HTTPException(status_code=403, detail="Not allowed")
    target_user = db.query(User).filter(User.username == username.strip()).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    target_member = _get_member(db, club.id, target_user.id)
    if not target_member:
        raise HTTPException(status_code=404, detail="Not a member")
    if target_member.role == "owner":
        raise HTTPException(status_code=403, detail="Cannot remove owner")
    if acting_role == "moderator" and target_member.role != "member":
        raise HTTPException(status_code=403, detail="Moderator can only remove members")
    if acting_role == "admin" and target_member.role == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot remove another admin")
    # owner can remove anyone except self handled via leave
    db.delete(target_member)
    db.commit()
    return None

@router.post("/{slug}/avatar", response_model=dict)
async def upload_club_avatar(slug: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    if not _can_edit(db, club, current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    _, url = save_image(data, file.content_type, subdir="clubs/avatars")
    club.avatar_url = url
    db.commit()
    return _club_to_read(club, db, current_user.id)

@router.post("/{slug}/cover", response_model=dict)
async def upload_club_cover(slug: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.slug == slug.strip()).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    if not _can_edit(db, club, current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    _, url = save_image(data, file.content_type, subdir="clubs/covers")
    club.cover_url = url
    db.commit()
    return _club_to_read(club, db, current_user.id)
