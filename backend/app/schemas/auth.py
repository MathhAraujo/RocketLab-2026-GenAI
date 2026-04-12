from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UsuarioAutenticado(BaseModel):
    username: str
    is_admin: bool
