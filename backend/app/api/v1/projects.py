"""Projects showcase — CRUD + image (STEP 12)."""

import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, OwnerPublic
from app.services.storage import save_image
from app.core.config import settings

router = APIRouter(tags=["projects"])

def _to_read(p: Project) -> dict:
    owner = None
    if p.owner:
        owner = {"id": p.owner.id, "username": p.owner.username, "display_name": p.owner.display_name, "avatar_url": p.owner.avatar_url}
    return {
        "id": p.id,
        "owner_id": p.owner_id,
        "owner": owner,
        "name": p.name,
        "description": p.description,
        "technologies": p.technologies or [],
        "github_url": p.github_url,
        "demo_url": p.demo_url,
        "image_url": p.image_url,
        "status": p.status,
        "position": p.position,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }

def _next_position(db: Session, owner_id: uuid.UUID) -> int:
    max_pos = db.query(func.max(Project.position)).filter(Project.owner_id == owner_id).scalar()
    return (max_pos or 0) + 1

@router.get("/users/me/projects", response_model=List[ProjectRead])
def list_my_projects(limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    limit = min(limit, 50)
    projects = db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.position.asc(), Project.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_read(p) for p in projects]

# --- public user projects ---
@router.get("/users/{username}/projects", response_model=List[ProjectRead])
def list_user_projects(username: str, limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = min(limit, 50)
    projects = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.position.asc(), Project.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_read(p) for p in projects]

@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_read(p)

@router.post("/users/me/projects", response_model=ProjectRead, status_code=201, dependencies=[Depends(rate_limit(limit=10, window=60, key_prefix="project_create", by_user=True))])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # ignore any owner_id from client — always current_user
    pos = _next_position(db, current_user.id)
    proj = Project(
        owner_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description.strip(),
        technologies=payload.technologies or [],
        github_url=payload.github_url,
        demo_url=payload.demo_url,
        status=payload.status,
        position=pos,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return _to_read(proj)

@router.patch("/users/me/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not project owner")
    if payload.name is not None:
        proj.name = payload.name.strip()
    if payload.description is not None:
        proj.description = payload.description.strip()
    if payload.technologies is not None:
        proj.technologies = payload.technologies
    if payload.github_url is not None or "github_url" in payload.model_fields_set:
        proj.github_url = payload.github_url
    if payload.demo_url is not None or "demo_url" in payload.model_fields_set:
        proj.demo_url = payload.demo_url
    if payload.status is not None:
        proj.status = payload.status
    db.commit()
    db.refresh(proj)
    return _to_read(proj)

@router.delete("/users/me/projects/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not project owner")
    # delete image best-effort
    old_url = proj.image_url
    db.delete(proj)
    db.commit()
    if old_url:
        try:
            # old_url like /uploads/projects/<file>
            fname = old_url.split("/")[-1]
            fpath = Path(settings.upload_dir) / "projects" / fname
            if fpath.exists():
                fpath.unlink()
        except Exception:
            pass
    return None

@router.post("/users/me/projects/{project_id}/image", response_model=ProjectRead)
async def upload_project_image(project_id: uuid.UUID, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not project owner")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    _, public_url = save_image(data, file.content_type, subdir="projects")
    old_url = proj.image_url
    proj.image_url = public_url
    db.commit()
    db.refresh(proj)
    # delete old file best-effort
    if old_url and old_url != public_url:
        try:
            fname = old_url.split("/")[-1]
            fpath = Path(settings.upload_dir) / "projects" / fname
            if fpath.exists():
                fpath.unlink()
        except Exception:
            pass
    return _to_read(proj)
