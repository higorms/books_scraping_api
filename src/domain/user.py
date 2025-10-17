from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass
class User:
    """Entidade de usuário."""
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    id: Optional[int] = None


class UserRepository(Protocol):
    """Protocolo para repositório de usuários."""
    def create(self, user: User) -> User: ...
    def get_by_username(self, username: str) -> Optional[User]: ...
    def get_by_email(self, email: str) -> Optional[User]: ...
    def update(self, user: User) -> User: ...
    def delete(self, username: str) -> bool: ...
