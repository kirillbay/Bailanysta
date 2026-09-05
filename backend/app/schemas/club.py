"""Club schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ClubCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

class ClubRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    avatar_url: str | None
    cover_url: str | None
    created_at: datetime
    updated_at: datetime
    members_count: int = 0
    is_member: bool = False
    role: str | None = None

class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    role: str
    joined_at: datetime
