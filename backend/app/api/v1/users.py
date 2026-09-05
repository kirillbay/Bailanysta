"""Profiles: public GET, own GET/PATCH, avatar/cover upload."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
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


@router.get("/{username}", response_model=UserPublic)
def get_public_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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
