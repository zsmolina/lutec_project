from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Lutec API"
    app_version: str = "0.1.0"

    openai_api_key: SecretStr | None = Field(default=None)
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.0

    max_zip_size_mb: int = 100
    max_formap_excel_mb: int = 50
    max_pdf_count: int = 500
    max_pdf_size_mb: int = 25
    job_ttl_hours: int = 24

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    temp_dir: Path | None = None

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def normalize_api_key(cls, value: str | SecretStr | None) -> str | SecretStr | None:
        if value is None:
            return None
        raw = value.get_secret_value() if isinstance(value, SecretStr) else str(value)
        cleaned = raw.strip().strip('"').strip("'")
        if cleaned in {"", "sk-...", "sk-proj-..."}:
            return None
        return cleaned

    @property
    def openai_configured(self) -> bool:
        return self.openai_api_key is not None

    @property
    def max_zip_size_bytes(self) -> int:
        return self.max_zip_size_mb * 1024 * 1024

    @property
    def max_formap_excel_bytes(self) -> int:
        return self.max_formap_excel_mb * 1024 * 1024

    @property
    def max_pdf_size_bytes(self) -> int:
        return self.max_pdf_size_mb * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_temp_dir(self) -> Path:
        path = self.temp_dir or (_BACKEND_ROOT / "storage" / "tmp")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_jobs_dir(self) -> Path:
        path = self.resolve_temp_dir() / "jobs"
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
