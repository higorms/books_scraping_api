import logging
from dataclasses import dataclass
from src.domain.book import BookRepository
from src.domain.exceptions import BookRepositoryException


@dataclass
class HealthStatus:
    """Classe que representa o status de saúde da aplicação."""
    status: str
    database_connection: bool
    message: str


class HealthCheck:
    """Caso de uso para verificação de saúde da aplicação."""

    def __init__(self, repository: BookRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self) -> HealthStatus:
        """Executa a verificação de saúde da aplicação."""
        try:
            self.logger.info("Iniciando verificação de saúde da aplicação")

            # Testa conectividade com os dados tentando obter uma lista
            self.repository.get_all_books()

            self.logger.info("Verificação de saúde concluída com sucesso")
            return HealthStatus(
                status="ok",
                database_connection=True,
                message="Aplicação funcionando corretamente"
            )

        except BookRepositoryException as e:
            self.logger.warning(
                f"Problema na conectividade com dados: {e.message}"
                )
            return HealthStatus(
                status="Não ok",
                database_connection=False,
                message=f"Problema na conectividade com dados: {e.message}"
            )
        except Exception as e:
            self.logger.error(
                f"Erro inesperado durante verificação de saúde: {e}"
                )
            return HealthStatus(
                status="Não ok",
                database_connection=False,
                message=f"Erro inesperado: {str(e)}"
            )
