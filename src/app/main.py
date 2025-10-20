import logging
import sys
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from src.app.routes.book_routes import router as book_router
from src.app.routes.health_routes import router as health_router
from src.app.middleware.request_logging import RequestLoggingMiddleware
from src.infrastructure.services.datadog_config import configure_datadog


# Configuração do logging com formato JSON para Datadog
class DatadogJsonFormatter(logging.Formatter):
    """Formatter personalizado para logs em formato JSON compatível com Datadog."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "dd.service": "books-scraping-api",
            "dd.env": "production",
            "dd.version": "1.0.0"
        }

        if record.exc_info:
            log_data["error.kind"] = record.exc_info[0].__name__
            log_data["error.message"] = str(record.exc_info[1])
            log_data["error.stack"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# Configuração do logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(DatadogJsonFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger(__name__)

# Configura Datadog
if configure_datadog():
    logger.info("Datadog habilitado e configurado")
else:
    logger.warning("Datadog não foi configurado")

app = FastAPI(
    title="Books Scraping API",
    description="API para gerenciamento de catálogo de livros extraídos "
                "via web scraping",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona middleware de logging de requisições
app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas.

    Args:
        request (Request): Requisição que causou a exceção.
        exc (Exception): Exceção capturada.

    Returns:
        JSONResponse: Resposta JSON com erro padronizado.
    """
    logger.error(f"Erro não tratado na rota {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "path": str(request.url)
        }
    )


app.include_router(book_router, prefix="/api")
app.include_router(health_router, prefix="/api")


def main():
    """Função principal para inicialização do servidor da aplicação.

    Configura e inicia o servidor Uvicorn com as configurações
    de desenvolvimento, incluindo hot reload e binding local.

    Raises:
        Exception: Em caso de erro na inicialização do servidor.
    """
    try:
        logger.info("Iniciando servidor da aplicação Books Scraping API")
        uvicorn.run(
            "src.app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
