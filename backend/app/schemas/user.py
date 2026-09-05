"""Pydantic schemas for User."""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    cover_url: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    """Public profile — no email, no secrets."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    cover_url: str | None
    created_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    # avatar_url/cover_url are set via upload endpoints, not directly patchable to avoid SSRF
