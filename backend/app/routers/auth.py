from fastapi import APIRouter

from app.schemas.auth import LoginRequest, TokenResponse, UsuarioAutenticado

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Mock: aceita qualquer credencial. Auth real será implementada futuramente."""
    return TokenResponse(access_token="mock-token", token_type="bearer")


@router.get("/me", response_model=UsuarioAutenticado)
def me():
    """Retorna o usuário autenticado mockado."""
    return UsuarioAutenticado(username="admin")
