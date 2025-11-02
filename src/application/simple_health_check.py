"""Caso de uso para health check simples."""
import logging
from dataclasses import dataclass


@dataclass
class SimpleHealthStatus:
    """Classe que representa o status simples de saúde."""
    status: str


class SimpleHealthCheck:
    """Caso de uso para verificação simples de saúde da aplicação.

    Este use case é otimizado para ser rápido e leve, usado principalmente
    pelo healthcheck do Docker. Apenas verifica se a aplicação está
    respondendo requisições HTTP.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self) -> SimpleHealthStatus:
        """Executa verificação simples de saúde.

        Returns:
            SimpleHealthStatus: Status indicando que a aplicação está up.
        """
        self.logger.debug("Health check simples executado")
        return SimpleHealthStatus(status="ok")
