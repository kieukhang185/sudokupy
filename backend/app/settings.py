import os
from typing import Optional
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Sudokupy API")
    app_env: str = os.getenv("APP_ENV", "dev")  # dev|staging|prod
    app_debug: bool = bool(
        os.getenv("APP_DEBUG", "true").lower() in ("1", "true", "yes")
    )
    app_version: str = os.getenv("APP_VERSION", "0.1.0")

    database_url: Optional[str] = os.getenv("DATABASE_URL")  # If set, overrides below
    db_host: str = os.getenv("POSTGRES_HOST", "localhost")
    db_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db_name: str = os.getenv("POSTGRES_DB", "sudokupy")
    db_user: str = os.getenv("POSTGRES_USER", "postgres")
    db_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

    @computed_field(return_type=str)
    def db_url(self) -> str:
        # tests override
        # if self.test_database_url:
        #     return self.test_database_url.strip()

        # explicit URL
        if self.database_url:
            url = self.database_url.strip().strip("'").strip('"')
            if url.startswith("postgres://"):
                url = "postgresql+psycopg2://" + url[len("postgres://") :]
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url

        # compose from parts
        if self.db_user and self.db_password and self.db_name:
            pw = quote_plus(self.db_password)
            return f"postgresql+psycopg2://{self.db_user}:{pw}@{self.db_host}:{self.db_port}/{self.db_name}"

        # fallback
        return "sqlite:///./app.db"

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
