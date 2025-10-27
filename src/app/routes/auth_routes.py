import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    UserCreateResponse
)
from src.infrastructure.security.jwt_service import JWTService
from src.infrastructure.database import get_user_repository
from src.application.register_user import (
    RegisterUser,
    UserAlreadyExistsError
)
from src.application.login_user import (
    LoginUser,
    InvalidCredentialsError,
    UserInactiveError
)
from src.domain.user import UserRepository


router = APIRouter()
logger = logging.getLogger(__name__)


def get_jwt_service() -> JWTService:
    """Factory para o serviço JWT."""
    return JWTService()


@router.post(
    "/v1/auth/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário no sistema.",
    tags=["Autenticação"],
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Usuário ou email já existe"},
        500: {"description": "Erro interno do servidor"}
    }
)
def register(
    user_data: RegisterRequest,
    repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    try:
        logger.info(
            f"Tentativa de registro para usuário: {user_data.username}"
        )

        # Executar caso de uso de registro
        register_use_case = RegisterUser(repository, jwt_service)
        user = register_use_case.execute(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )

        logger.info(f"Usuário registrado com sucesso: {user.username}")
        return UserCreateResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )

    except UserAlreadyExistsError as e:
        logger.warning(f"Tentativa de registro duplicado: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro inesperado no registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


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
    repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    try:
        logger.info(f"Tentativa de login para usuário: {login_data.username}")

        # Executar caso de uso de login
        login_use_case = LoginUser(repository, jwt_service)
        token_data = login_use_case.execute(
            username=login_data.username,
            password=login_data.password
        )

        return TokenResponse(
            access_token=token_data["access_token"],
            expires_in=token_data["expires_in"]
        )

    except (InvalidCredentialsError, UserInactiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro inesperado no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
