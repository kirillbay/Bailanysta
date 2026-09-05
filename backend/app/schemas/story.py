"""Story schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class AuthorPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None

class StoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    author_id: uuid.UUID
    author: AuthorPublic | None = None
    media_url: str | None
    media_type: str | None
    text: str | None
    created_at: datetime
    expires_at: datetime

class StoryGroup(BaseModel):
    author: AuthorPublic
    stories: list[StoryRead]
