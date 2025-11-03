import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.application.health_check import HealthCheck
from src.application.simple_health_check import SimpleHealthCheck
from src.infrastructure.repositories.book_csv_repository import BookRepository
from src.app.schemas.health_schema import HealthSchema
from src.app.schemas.simple_health_schema import SimpleHealthSchema
from src.infrastructure.repositories.pinecone_repository import (
    PineconeRepository
)


router = APIRouter()
logger = logging.getLogger(__name__)


def get_simple_health_check_use_case() -> SimpleHealthCheck:
    """Factory function para criar instância do caso de uso SimpleHealthCheck.

    Este use case é leve e não tem dependências externas.
    """
    return SimpleHealthCheck()


def get_health_check_use_case() -> HealthCheck:
    """Factory function para criar instância do caso de uso HealthCheck."""
    try:
        repository = BookRepository("data/books.csv")

        # Tentar inicializar Pinecone (opcional)
        pinecone_repo = None
        try:
            pinecone_repo = PineconeRepository()
        except Exception as e:
            logger.warning(f"Pinecone não disponível: {e}")

        return HealthCheck(repository, pinecone_repo)

    except Exception as e:
        logger.error(f"Erro ao configurar dependências do health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao configurar dependências"
        )


@router.get(
    "/v1/health/simple",
    response_model=SimpleHealthSchema,
    summary="Health check simples",
    description="Endpoint otimizado para Docker healthcheck. "
                "Verifica apenas se o servidor está respondendo.",
    tags=["Health"],
    responses={
        200: {"description": "Servidor está respondendo"}
    }
)
def simple_health_check(
    use_case: SimpleHealthCheck = Depends(get_simple_health_check_use_case)
):
    """Health check simples para Docker.

    Este endpoint segue a arquitetura do projeto usando use cases
    e dependency injection, mas é otimizado para ser rápido e leve.
    Não faz verificações de conectividade com serviços externos.

    Args:
        use_case: Caso de uso SimpleHealthCheck injetado via Depends.

    Returns:
        SimpleHealthStatus: Status indicando que o servidor está up.
    """
    try:
        logger.debug("Processando requisição de health check simples")
        health_status = use_case.execute()
        return health_status.__dict__
    except Exception as e:
        logger.error(f"Erro inesperado durante health check simples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/v1/health",
    response_model=HealthSchema,
    summary="Verificação de saúde da aplicação",
    description="Retorna o status da aplicação e conectividade com os "
                "serviços.",
    tags=["Health"],
    responses={
        200: {"description": "Aplicação saudável"},
        503: {"description": "Aplicação com problemas de conectividade"},
        500: {"description": "Erro interno do servidor"}
    }
)
def health_check(use_case: HealthCheck = Depends(get_health_check_use_case)):
    try:
        logger.info("Processando requisição de health check")
        health_status = use_case.execute()

        if health_status.status == "healthy":
            logger.info("Health check concluído: aplicação saudável")
            return health_status.__dict__
        else:
            logger.warning(f"Health check concluído: {health_status.message}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status.__dict__
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado durante health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor durante verificação de saúde"
        )
