"""Configurações da aplicação carregadas via pydantic-settings."""

from __future__ import annotations

import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração centralizada lida de variáveis de ambiente e arquivo .env."""

    DATABASE_URL: str = "sqlite:///./database.db"
    JWT_SECRET: str = Field(default_factory=lambda: secrets.token_hex(32))
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    GOOGLE_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
