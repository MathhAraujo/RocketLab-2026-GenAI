"""Dependências FastAPI para autenticação e autorização de perfis."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario
from app.security import ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Decodificar o JWT e retornar o usuário autenticado ou levantar 401.

    Args:
        token: Bearer token extraído do header Authorization.
        db: Sessão do banco de dados injetada pelo FastAPI.

    Returns:
        Instância de ``Usuario`` correspondente ao token.

    Raises:
        HTTPException: 401 se o token for inválido, expirado ou o usuário não existir.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verificar se o usuário autenticado possui perfil administrador ou levantar 403.

    Args:
        current_user: Usuário autenticado injetado por ``get_current_user``.

    Returns:
        O mesmo ``Usuario`` se for administrador.

    Raises:
        HTTPException: 403 se o usuário não tiver permissão de administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios insuficientes para realizar esta ação.",
        )
    return current_user
