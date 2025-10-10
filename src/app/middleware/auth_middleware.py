import logging
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.security.jwt_service import JWTService


logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_jwt_service() -> JWTService:
    """Factory para o serviço JWT."""
    return JWTService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> dict:
    """Dependency para obter o usuário atual a partir do token JWT.

    Args:
        credentials: Credenciais de autorização
        jwt_service: Serviço JWT

    Returns:
        dict: Dados do usuário atual

    Raises:
        HTTPException: Se o token for inválido
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt_service.verify_token(token)

        if payload is None:
            logger.warning("Token JWT inválido ou expirado")
            raise credentials_exception

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        return {"username": username, "payload": payload}

    except Exception as e:
        logger.error(f"Erro na validação do token: {e}")
        raise credentials_exception


async def require_auth(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency que requer autenticação.

    Args:
        current_user: Usuário atual obtido do token

    Returns:
        dict: Dados do usuário autenticado
    """
    return current_user
