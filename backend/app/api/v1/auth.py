"""Authentication endpoints: register, login, me, logout."""

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, verify_password, create_access_token, set_auth_cookie, clear_auth_cookie
from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str) -> str:
    return username.strip()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    username = _normalize_username(payload.username)
    email = _normalize_email(str(payload.email))

    # Check duplicates explicitly for clean 409
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Extra length guard (avoid huge payloads)
    if len(payload.password) > 128:
        raise HTTPException(status_code=400, detail="Password too long")

    hashed = hash_password(payload.password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed,
        display_name=payload.display_name.strip() if payload.display_name else None,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        # Race condition fallback
        raise HTTPException(status_code=409, detail="Username or email already taken")

    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.post("/login", response_model=UserRead)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    identifier = payload.identifier.strip()
    is_email = "@" in identifier

    user: User | None = None
    if is_email:
        email = _normalize_email(identifier)
        user = db.query(User).filter(User.email == email).first()
    else:
        username = _normalize_username(identifier)
        user = db.query(User).filter(User.username == username).first()

    # Uniform error to avoid user enumeration
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update updated_at touch handled by DB; no need explicit

    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, current_user: User = Depends(get_current_user)):
    clear_auth_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
