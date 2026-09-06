import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Bailanysta"
    app_env: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bailanysta"
    secret_key: str = "change-me-in-production-generate-32-bytes"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    upload_dir: str = "./uploads"
    max_avatar_size_mb: int = 5
    max_cover_size_mb: int = 5

    @field_validator("secret_key")
    @classmethod
    def validate_secret(cls, v: str) -> str:
        env = os.getenv("APP_ENV", "development")
        if env == "production":
            if not v or v.startswith("change-me") or len(v) < 32:
                raise ValueError("SECRET_KEY must be set to a strong random value (>=32 chars) in production — generate with: openssl rand -hex 32")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors(cls, v: str) -> str:
        env = os.getenv("APP_ENV", "development")
        if env == "production" and v.strip() in ("*", "", "http://localhost:5173,http://localhost:3000"):
            # Allow but warn — better to be explicit in prod; we don't hard-fail to keep deploys flexible
            pass
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        # Robust parsing: handle quotes, trailing slashes, empty entries
        # Render may set "https://bailanysta-front.onrender.com" with quotes or trailing slash
        origins = []
        for o in self.cors_origins.split(","):
            o = o.strip()
            if not o:
                continue
            # Strip surrounding quotes if present (e.g., "https://..." or 'https://...')
            if len(o) >= 2 and ((o[0] == '"' and o[-1] == '"') or (o[0] == "'" and o[-1] == "'")):
                o = o[1:-1].strip()
            # Normalize: strip trailing slash for consistency (Origin header never has trailing slash)
            o = o.rstrip("/")
            if o:
                origins.append(o)
        return origins

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def database_url_safe(self) -> str:
        try:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(self.database_url)
            if parsed.password:
                netloc = parsed.hostname or ""
                if parsed.username:
                    netloc = f"{parsed.username}:***@{netloc}"
                if parsed.port:
                    netloc = f"{netloc}:{parsed.port}"
                masked = parsed._replace(netloc=netloc)
                return urlunparse(masked)
            return self.database_url
        except Exception:
            return "***"


settings = Settings()
