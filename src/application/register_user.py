import logging
from src.domain.user import User, UserRepository
from src.infrastructure.security.jwt_service import JWTService
from src.domain.exceptions import BookScrapingAPIException


class UserAlreadyExistsError(BookScrapingAPIException):
    """Exceção quando usuário já existe."""
    pass


class RegisterUser:
    """Caso de uso para registro de usuário."""

    def __init__(self, repository: UserRepository, jwt_service: JWTService):
        self.repository = repository
        self.jwt_service = jwt_service
        self.logger = logging.getLogger(__name__)

    def execute(self, username: str, email: str, password: str) -> User:
        """Registra um novo usuário."""
        # Verificar se usuário já existe
        if self.repository.get_by_username(username):
            raise UserAlreadyExistsError(f"Usuário {username} já existe")

        if self.repository.get_by_email(email):
            raise UserAlreadyExistsError(f"Email {email} já está em uso")

        # Criar hash da senha
        hashed_password = self.jwt_service.hash_password(password)

        # Criar usuário
        user = User(
            id=None,
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )

        return self.repository.create(user)
