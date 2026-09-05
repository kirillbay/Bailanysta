"""Post schemas."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AuthorPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None

class PostMediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    url: str
    mime_type: str
    position: int

class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime
    author: AuthorPublic
    media: list[PostMediaRead] = []
    hashtags: list[str] = []

class PostCreateInput(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class PostUpdateInput(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
