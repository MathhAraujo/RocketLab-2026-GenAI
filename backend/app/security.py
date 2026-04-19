"""Utilitários de hash de senha e geração de tokens JWT."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Final

import bcrypt
import jwt

from app.config import settings

ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 60 * 24 * 7  # 1 semana


def get_password_hash(password: str) -> str:
    """Retornar o hash bcrypt da senha fornecida."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar se a senha em texto plano corresponde ao hash armazenado."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict[str, Any]) -> str:
    """Criar e assinar um JWT com os dados fornecidos e prazo de expiração padrão."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
