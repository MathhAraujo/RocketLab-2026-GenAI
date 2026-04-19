"""Schemas Pydantic para autenticação: login, registro e resposta de token."""

from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Payload de login com credenciais do usuário."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Payload de registro de novo usuário."""

    username: str
    password: str
    is_admin: bool = False


class TokenResponse(BaseModel):
    """Resposta contendo o JWT e o tipo do token."""

    access_token: str
    token_type: str


class UsuarioAutenticado(BaseModel):
    """Dados públicos do usuário autenticado retornados pela API."""

    username: str
    is_admin: bool
