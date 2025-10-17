import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.app.schemas.auth_schema import LoginRequest, TokenResponse, UserSchema
from src.infrastructure.security.jwt_service import JWTService
from src.app.middleware.auth_middleware import require_auth


router = APIRouter()
logger = logging.getLogger(__name__)


def get_jwt_service() -> JWTService:
    """Factory para o serviço JWT."""
    return JWTService()


# Simulação de banco de usuários
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "is_active": True,
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "is_active": True,
    }
}


@router.post(
    "/v1/auth/login",
    response_model=TokenResponse,
    summary="Realizar login",
    description="Autentica o usuário e retorna um token JWT.",
    tags=["Autenticação"],
    responses={
        200: {"description": "Login realizado com sucesso"},
        401: {"description": "Credenciais inválidas"},
        500: {"description": "Erro interno do servidor"}
    }
)
def login(
    login_data: LoginRequest,
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """Endpoint para autenticação de usuário."""
    try:
        logger.info(f"Tentativa de login para usuário: {login_data.username}")

        # Verificar se o usuário existe
        user = fake_users_db.get(login_data.username)
        if not user:
            logger.warning(f"Usuário não encontrado: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        # Verificar senha
        if not jwt_service.verify_password(login_data.password, user["hashed_password"]):
            logger.warning(f"Senha incorreta para usuário: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        # Criar token
        access_token = jwt_service.create_access_token(
            data={"sub": user["username"], "email": user["email"]}
        )

        logger.info(f"Login bem-sucedido para usuário: {login_data.username}")
        return TokenResponse(
            access_token=access_token,
            expires_in=jwt_service.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/v1/auth/me",
    response_model=UserSchema,
    summary="Obter dados do usuário atual",
    description="Retorna os dados do usuário autenticado.",
    tags=["Autenticação"],
    responses={
        200: {"description": "Dados do usuário obtidos com sucesso"},
        401: {"description": "Token inválido ou expirado"}
    }
)
async def get_current_user_info(current_user: dict = Depends(require_auth)):
    """Endpoint para obter informações do usuário atual."""
    username = current_user["username"]
    user_data = fake_users_db.get(username)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return UserSchema(
        username=user_data["username"],
        email=user_data["email"],
        is_active=user_data["is_active"]
    )
