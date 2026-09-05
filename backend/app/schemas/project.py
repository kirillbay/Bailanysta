"""Project schemas — validation per STEP 12 spec."""

import uuid
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, ConfigDict

ALLOWED_STATUSES = ("idea", "in_progress", "completed", "archived")
MAX_TECH = 20
MAX_TECH_LEN = 50
ALLOWED_GITHUB_HOSTS = {"github.com", "www.github.com"}


def _validate_url(url: str | None, *, github_only: bool = False) -> str | None:
    if url is None:
        return None
    url = url.strip()
    if not url:
        return None
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ("https", "http"):
        raise ValueError("URL must start with https:// or http://")
    if scheme not in ("https", "http"):
        raise ValueError("Invalid URL scheme")
    # reject javascript/data/file
    if parsed.scheme.lower() in ("javascript", "data", "file"):
        raise ValueError("Invalid URL scheme")
    if not parsed.netloc:
        raise ValueError("Invalid URL")
    if github_only:
        host = parsed.hostname or ""
        host = host.lower()
        if host not in ALLOWED_GITHUB_HOSTS:
            raise ValueError("github_url must be on github.com")
    return url


def _normalize_technologies(v):
    if v is None:
        return []
    if not isinstance(v, list):
        raise ValueError("technologies must be a list")
    if len(v) > MAX_TECH:
        raise ValueError(f"max {MAX_TECH} technologies")
    cleaned = []
    seen = set()
    for item in v:
        if not isinstance(item, str):
            raise ValueError("technology must be string")
        t = item.strip()
        if not t:
            continue
        if len(t) > MAX_TECH_LEN:
            raise ValueError(f"technology max {MAX_TECH_LEN} chars")
        low = t.lower()
        if low in seen:
            continue
        seen.add(low)
        cleaned.append(t)
    if len(cleaned) > MAX_TECH:
        raise ValueError(f"max {MAX_TECH} technologies")
    return cleaned


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=2000)
    technologies: list[str] = Field(default_factory=list)
    github_url: Optional[str] = Field(default=None, max_length=512)
    demo_url: Optional[str] = Field(default=None, max_length=512)
    status: str = Field(default="idea", max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        if len(v) > 150:
            raise ValueError("name too long")
        return v

    @field_validator("description")
    @classmethod
    def validate_desc(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description must not be empty")
        if len(v) > 2000:
            raise ValueError("description too long")
        return v

    @field_validator("technologies", mode="before")
    @classmethod
    def validate_tech(cls, v):
        return _normalize_technologies(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {', '.join(ALLOWED_STATUSES)}")
        return v

    @field_validator("github_url", mode="before")
    @classmethod
    def validate_github(cls, v):
        if v is None or v == "":
            return None
        return _validate_url(v, github_only=True)

    @field_validator("demo_url", mode="before")
    @classmethod
    def validate_demo(cls, v):
        if v is None or v == "":
            return None
        return _validate_url(v, github_only=False)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    technologies: Optional[list[str]] = None
    github_url: Optional[str] = Field(default=None, max_length=512)
    demo_url: Optional[str] = Field(default=None, max_length=512)
    status: Optional[str] = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_desc(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("description must not be empty")
        if len(v) > 2000:
            raise ValueError("description too long")
        return v

    @field_validator("technologies", mode="before")
    @classmethod
    def validate_tech(cls, v):
        if v is None:
            return None
        return _normalize_technologies(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {', '.join(ALLOWED_STATUSES)}")
        return v

    @field_validator("github_url", mode="before")
    @classmethod
    def validate_github(cls, v):
        if v is None or v == "":
            return None
        # allow explicit null to clear
        return _validate_url(v, github_only=True)

    @field_validator("demo_url", mode="before")
    @classmethod
    def validate_demo(cls, v):
        if v is None or v == "":
            return None
        return _validate_url(v, github_only=False)


class OwnerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str
    display_name: str | None = None
    avatar_url: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    owner: Optional[OwnerPublic] = None
    name: str
    description: str
    technologies: list[str]
    github_url: str | None = None
    demo_url: str | None = None
    image_url: str | None = None
    status: str
    position: int
    created_at: datetime
    updated_at: datetime
