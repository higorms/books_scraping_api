from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema para requisição de login."""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Schema para requisição de registro de usuário."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nome de usuário único"
    )
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(
        ...,
        min_length=6,
        description="Senha com no mínimo 6 caracteres"
    )


class TokenResponse(BaseModel):
    """Schema para resposta do token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreateResponse(BaseModel):
    """Schema para resposta de criação de usuário."""
    id: int
    username: str
    email: str
    is_active: bool
    message: str = "Usuário criado com sucesso"
