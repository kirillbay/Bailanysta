"""Auth request schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, description="email or username")
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    """Auth response with user and access token for cross-site fallback."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"
