import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.application.health_check import HealthCheck
from src.infrastructure.repositories.book_csv_repository import BookRepository
from src.app.schemas.health_schema import HealthSchema


router = APIRouter()
logger = logging.getLogger(__name__)


def get_health_check_use_case() -> HealthCheck:
    """Factory function para criar instância do caso de uso HealthCheck."""
    try:
        repository = BookRepository("data/books.csv")
        return HealthCheck(repository)
    except Exception as e:
        logger.error(f"Erro ao configurar dependências do health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao configurar dependências"
        )


@router.get(
    "/v1/health",
    response_model=HealthSchema,
    summary="Verificação de saúde da aplicação",
    description="Retorna o status da aplicação e conectividade com os dados.",
    tags=["Health"],
    responses={
        200: {"description": "Status de saúde recuperado com sucesso"},
        503: {"description": "Aplicação com problemas de conectividade"},
        500: {"description": "Erro interno do servidor"}
    }
)
def health_check(use_case: HealthCheck = Depends(get_health_check_use_case)):
    """Endpoint para verificação de saúde da aplicação."""
    try:
        logger.info("Processando requisição de health check")
        health_status = use_case.execute()

        if health_status.status == "ok":
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
