"""Configuração do banco de dados SQLite."""
from pathlib import Path
from src.infrastructure.repositories.user_repository import UserSQLRepository


def get_database_url() -> str:
    """Retorna a URL do banco de dados."""
    # Criar diretório data se não existir
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Caminho do banco SQLite
    db_path = data_dir / "users.db"
    return f"sqlite:///{db_path}"


def get_user_repository() -> UserSQLRepository:
    """Factory para criar instância do repositório de usuários."""
    database_url = get_database_url()
    return UserSQLRepository(database_url)
