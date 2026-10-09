"""Cấu hình service, đọc từ biến môi trường hoặc file .env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[2]   # ai-service/
REPO_DIR = SERVICE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=SERVICE_DIR / ".env", env_file_encoding="utf-8",
        env_ignore_empty=False, extra="ignore",
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    ai_timeout_s: float = 30.0
    ai_force_fallback: bool = False
    ai_thinking_budget: int | None = None

    database_url: str = ""
    # Read catalog tables in the Spring database; cache/log storage remains separately configured.
    catalog_database_url: str = ""
    # Spring sends its own catalog with every integration request.
    backend_compat_only: bool = False
    data_dir: Path = SERVICE_DIR / "data"
    figure_dir: Path = REPO_DIR / "frontend" / "public" / "figure"
    prompts_dir: Path = SERVICE_DIR / "prompts"
    prompt_templates: dict[str, str] = {}

    admin_token: str = "dev-admin-token"
    enable_dev_routes: bool = True
    rate_limit_per_min: int = 10
    cache_ttl_s: int = 7 * 24 * 3600
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def use_postgres(self) -> bool:
        return bool(self.database_url)

    @property
    def gemini_enabled(self) -> bool:
        return bool(self.gemini_api_key) and not self.ai_force_fallback


@lru_cache
def get_settings() -> Settings:
    return Settings()
