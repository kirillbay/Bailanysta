"""Stories API — 24h ephemeral."""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_current_user
from app.database.session import get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.models.story import Story
from app.models.follow import Follow
from app.services.storage import save_story_media
from app.core.config import settings

router = APIRouter(prefix="/stories", tags=["stories"])

def _story_to_read(s: Story):
    return {
        "id": s.id, "author_id": s.author_id,
        "author": {"id": s.author.id, "username": s.author.username, "display_name": s.author.display_name, "avatar_url": s.author.avatar_url} if s.author else None,
        "media_url": s.media_url, "media_type": s.media_type, "text": s.text,
        "created_at": s.created_at, "expires_at": s.expires_at
    }

@router.post("", dependencies=[Depends(rate_limit(limit=10, window=60, key_prefix="story_create", by_user=True))], response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_story(
    file: UploadFile = File(None),
    text: str = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # text validation
    if text is not None:
        text = text.strip()
        if len(text) > 2000:
            raise HTTPException(status_code=422, detail="Text too long (max 2000)")
        if text == "":
            text = None
    if file is None or not file.filename:
        # text-only not supported for MVP if no media, require media
        raise HTTPException(status_code=422, detail="Media file required")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    # author_id not accepted from client
    try:
        fs_path, public_url, media_type = save_story_media(data, file.content_type)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file")

    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)
    story = Story(author_id=current_user.id, media_url=public_url, media_type=media_type, text=text, created_at=now, expires_at=expires)
    db.add(story)
    db.commit()
    db.refresh(story)
    story = db.query(Story).filter(Story.id == story.id).first()
    return _story_to_read(story)

@router.get("", response_model=list)
def list_stories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    # Followed users + own
    followed_ids = [r[0] for r in db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()]
    allowed_ids = set(followed_ids + [current_user.id])
    stories = db.query(Story).filter(Story.expires_at > now, Story.author_id.in_(allowed_ids)).order_by(Story.created_at.desc()).all()
    # group by author
    groups = {}
    order = []
    for s in stories:
        aid = str(s.author_id)
        if aid not in groups:
            groups[aid] = {"author": {"id": s.author.id, "username": s.author.username, "display_name": s.author.display_name, "avatar_url": s.author.avatar_url} if s.author else None, "stories": []}
            order.append(aid)
    for s in stories:
        groups[str(s.author_id)]["stories"].append(_story_to_read(s))
    # ensure own first if exists
    own_key = str(current_user.id)
    if own_key in order:
        order.remove(own_key)
        order.insert(0, own_key)
    return [groups[k] for k in order]

@router.get("/{story_id}")
def get_story(story_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    now = datetime.now(timezone.utc)
    exp = story.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp <= now:
        raise HTTPException(status_code=404, detail="Story expired")
    # privacy: only own or followed
    if story.author_id != current_user.id:
        is_followed = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.following_id == story.author_id).first()
        if not is_followed:
            raise HTTPException(status_code=404, detail="Story not found")
    return _story_to_read(story)

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    if story.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    url = story.media_url
    db.delete(story)
    db.commit()
    if url and url.startswith("/uploads/"):
        try:
            fs_path = Path(settings.upload_dir) / url.replace("/uploads/", "", 1)
            if fs_path.exists():
                fs_path.unlink(missing_ok=True)
        except Exception:
            pass
    return None
