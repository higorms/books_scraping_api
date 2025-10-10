from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Schema para requisição de login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema para resposta do token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserSchema(BaseModel):
    """Schema para dados do usuário."""
    username: str
    email: Optional[str] = None
    is_active: bool = True
