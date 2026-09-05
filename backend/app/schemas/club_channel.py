"""Channel and message schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ChannelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

class ChannelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

class ChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    club_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    position: int
    created_at: datetime
    updated_at: datetime

class AuthorPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class MessageUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    channel_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    author: AuthorPublic | None = None
