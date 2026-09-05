from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Bailanysta"
    app_env: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    # origins as comma-separated string in .env, parsed to list
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Production: PostgreSQL via psycopg (SQLAlchemy 2.x): postgresql+psycopg://user:pass@host:5432/db
    # Legacy sqlite placeholder removed — see .env.example; value comes from env
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bailanysta"
    secret_key: str = "change-me-in-production-generate-32-bytes"

    # Optional: used only for health info, never logged with credentials
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def database_url_safe(self) -> str:
        """Return DB URL with password masked for logging."""
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
