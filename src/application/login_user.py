"""Caso de uso para autenticação de usuário."""
import logging
from src.domain.user import UserRepository
from src.infrastructure.security.jwt_service import JWTService
from src.domain.exceptions import BookScrapingAPIException


class InvalidCredentialsError(BookScrapingAPIException):
    """Exceção quando as credenciais são inválidas."""
    pass


class UserInactiveError(BookScrapingAPIException):
    """Exceção quando o usuário está inativo."""
    pass


class LoginUser:
    """Caso de uso para login de usuário."""

    def __init__(self, repository: UserRepository, jwt_service: JWTService):
        self.repository = repository
        self.jwt_service = jwt_service
        self.logger = logging.getLogger(__name__)

    def execute(self, username: str, password: str) -> dict:
        """Autentica um usuário e retorna token de acesso.

        Args:
            username: Nome de usuário
            password: Senha em texto plano

        Returns:
            dict: Contendo access_token e expires_in

        Raises:
            InvalidCredentialsError: Quando credenciais são inválidas
            UserInactiveError: Quando usuário está inativo
        """
        # Buscar usuário
        user = self.repository.get_by_username(username)
        if not user:
            self.logger.warning(f"Usuário não encontrado: {username}")
            raise InvalidCredentialsError("Credenciais inválidas")

        # Verificar se usuário está ativo
        if not user.is_active:
            self.logger.warning(
                f"Tentativa de login com usuário inativo: {username}"
            )
            raise UserInactiveError("Usuário inativo")

        # Verificar senha
        password_valid = self.jwt_service.verify_password(
            password, user.hashed_password
        )
        if not password_valid:
            self.logger.warning(f"Senha incorreta para usuário: {username}")
            raise InvalidCredentialsError("Credenciais inválidas")

        # Criar token
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.username, "email": user.email}
        )

        self.logger.info(f"Login bem-sucedido para usuário: {username}")

        return {
            "access_token": access_token,
            "expires_in": self.jwt_service.access_token_expire_minutes * 60
        }
