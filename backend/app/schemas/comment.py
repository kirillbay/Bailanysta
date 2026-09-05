"""Comment schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AuthorPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None

class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime
    author: AuthorPublic | None = None

class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
