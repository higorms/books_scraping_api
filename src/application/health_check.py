import logging
import os
from typing import Optional
from dataclasses import dataclass
from src.domain.book import BookRepository
from src.domain.exceptions import BookRepositoryException
from src.infrastructure.repositories.pinecone_repository import (
    PineconeRepository
    )


@dataclass
class HealthStatus:
    """Classe que representa o status de saúde da aplicação."""
    status: str
    database_connection: bool
    vector_database_connection: bool
    message: str


class HealthCheck:
    """Caso de uso para verificação de saúde da aplicação."""

    def __init__(self,
                 repository: BookRepository,
                 pinecone_repository: Optional[PineconeRepository] = None
                 ):
        self.repository = repository
        self.pinecone_repository = pinecone_repository
        self.logger = logging.getLogger(__name__)

    def execute(self) -> HealthStatus:
        """Executa a verificação de saúde da aplicação."""
        try:
            self.logger.info("Iniciando verificação de saúde da aplicação")

            # Teste de conectividade com dados CSV
            csv_status = self._check_csv_connection()

            # Teste de conectividade com Pinecone
            pinecone_status = (
                self._check_pinecone_connection()
                if self.pinecone_repository else True
            )

            overall_status = csv_status and pinecone_status

            result = HealthStatus(
                status="healthy" if overall_status else "unhealthy",
                database_connection=csv_status,
                vector_database_connection=pinecone_status,
                message=self._get_health_message(
                    csv_status,
                    pinecone_status
                    )
            )

            self.logger.info(f"Verificação concluída: {result.status}")
            return result

        except BookRepositoryException as e:
            self.logger.warning(
                f"Problema na conectividade com dados: {e.message}"
                )
            return HealthStatus(
                status="unhealthy",
                database_connection=False,
                vector_database_connection=False,
                message=f"Problema na conectividade com dados: {e.message}"
            )
        except Exception as e:
            self.logger.error(
                f"Erro inesperado durante verificação de saúde: {e}"
                )
            return HealthStatus(
                status="unhealthy",
                database_connection=False,
                vector_database_connection=False,
                message=f"Erro inesperado: {str(e)}"
            )

    def _check_csv_connection(self) -> bool:
        """Verifica se o arquivo CSV existe e não está vazio."""
        try:
            csv_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'books.csv'
                )
            csv_path = os.path.abspath(csv_path)

            # Verifica se o arquivo existe
            if not os.path.exists(csv_path):
                self.logger.error(f"Arquivo CSV não encontrado: {csv_path}")
                return False

            # Verifica se o arquivo não está vazio
            if os.path.getsize(csv_path) == 0:
                self.logger.error(f"Arquivo CSV está vazio: {csv_path}")
                return False

            self.logger.info(f"Arquivo CSV verificado com sucesso: {csv_path}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao verificar arquivo CSV: {e}")
            return False

    def _check_pinecone_connection(self) -> bool:
        """Verifica conectividade com Pinecone."""
        try:
            if self.pinecone_repository:
                return self.pinecone_repository.health_check()
            return True
        except Exception as e:
            self.logger.error(f"Erro no health check do Pinecone: {e}")
            return False

    def _get_health_message(self,
                            csv_status: bool,
                            pinecone_status: bool) -> str:
        """Gera mensagem de status baseada nos testes."""
        if csv_status and pinecone_status:
            return "Aplicação funcionando corretamente"
        elif csv_status and not pinecone_status:
            return "Aplicação funcionando, mas banco vetorial indisponível"
        elif not csv_status and pinecone_status:
            return "Banco vetorial OK, mas dados CSV indisponíveis"
        else:
            return "Aplicação com problemas de conectividade"
