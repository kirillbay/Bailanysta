from pydantic_settings import BaseSettings, SettingsConfigDict
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

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

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
