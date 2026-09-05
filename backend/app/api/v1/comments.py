"""Comments endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post
from app.models.social import Comment
from app.schemas.comment import CommentRead, CommentCreate, CommentUpdate

router = APIRouter(tags=["comments"])

def _comment_to_read(c: Comment):
    return {
        "id": c.id,
        "post_id": c.post_id,
        "author_id": c.author_id,
        "content": c.content,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "author": {"id": c.author.id, "username": c.author.username, "display_name": c.author.display_name, "avatar_url": c.author.avatar_url} if c.author else None,
    }

@router.get("/posts/{post_id}/comments", response_model=list)
def list_comments(post_id: uuid.UUID, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).offset(offset).limit(min(limit,50)).all()
    return [_comment_to_read(c) for c in comments]

@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: uuid.UUID, payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not payload.content.strip():
        raise HTTPException(status_code=422, detail="Content cannot be empty")
    c = Comment(post_id=post_id, author_id=current_user.id, content=payload.content.strip())
    db.add(c)
    db.commit()
    db.refresh(c)
    c = db.query(Comment).filter(Comment.id == c.id).first()
    return _comment_to_read(c)

@router.patch("/comments/{comment_id}", response_model=CommentRead)
def update_comment(comment_id: uuid.UUID, payload: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if not payload.content.strip():
        raise HTTPException(status_code=422, detail="Content cannot be empty")
    c.content = payload.content.strip()
    db.commit()
    db.refresh(c)
    return _comment_to_read(c)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    db.delete(c)
    db.commit()
    return None
