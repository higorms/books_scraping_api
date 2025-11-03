"""Middleware para logging de requisições da Books Scraping API.

Este módulo contém middleware personalizado para logging detalhado
de todas as requisições HTTP, incluindo tempo de resposta e status codes.
"""

import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.infrastructure.services.datadog_config import (
    send_metric,
    increment_counter
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging automático de requisições HTTP.

    Registra informações detalhadas sobre cada requisição, incluindo:
    - Método HTTP e URL
    - Endereço IP do cliente
    - User-Agent
    - Tempo de processamento
    - Status code da resposta
    """

    def __init__(self, app, logger_name: str = __name__):
        """Inicializa o middleware de logging.

        Args:
            app: Aplicação FastAPI.
            logger_name (str): Nome do logger a ser utilizado.
        """
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Processa a requisição e registra informações de log.

        Args:
            request (Request): Requisição HTTP recebida.
            call_next (Callable): Próximo middleware ou handler.

        Returns:
            Response: Resposta HTTP processada.
        """
        # Captura informações da requisição
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        method = request.method
        url = str(request.url)

        # Log da requisição recebida
        self.logger.info(
            f"Requisição recebida: {method} {url} - "
            f"IP: {client_ip} - User-Agent: {user_agent}"
        )

        try:
            # Processa a requisição
            response = await call_next(request)

            # Calcula tempo de processamento
            process_time = time.time() - start_time

            # Log da resposta
            self.logger.info(
                f"Resposta enviada: {method} {url} - "
                f"Status: {response.status_code} - "
                f"Tempo: {process_time:.3f}s"
            )

            # Envia métricas para o Datadog
            tags = [
                f"method:{method}",
                f"status:{response.status_code}",
                f"path:{request.url.path}"
            ]
            
            # Métrica de latência
            send_metric(
                "books.api.request.duration",
                process_time,
                tags=tags
            )
            
            # Contador de requisições
            increment_counter(
                "books.api.request.count",
                value=1,
                tags=tags
            )

            # Adiciona header com tempo de processamento
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # Log de erro durante processamento
            process_time = time.time() - start_time
            self.logger.error(
                f"Erro durante processamento: {method} {url} - "
                f"Erro: {str(e)} - Tempo: {process_time:.3f}s"
            )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extrai o endereço IP real do cliente.

        Considera headers de proxy como X-Forwarded-For e X-Real-IP.

        Args:
            request (Request): Requisição HTTP.

        Returns:
            str: Endereço IP do cliente.
        """
        # Verifica headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Pega o primeiro IP da lista (cliente original)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback para IP direto
        return request.client.host if request.client else "Unknown"
