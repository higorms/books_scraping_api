import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.app.routes.book_routes import get_book_repository
from src.domain.book import BookRepository

from src.application.get_ml_features import GetMLFeatures
from src.application.get_training_data import GetTrainingData
from src.application.run_prediction import RunPrediction

from src.app.schemas.ml_schema import (
    BookFeatureSchema,
    TrainingDataSchema,
    PredictionInputSchema,
    PredictionOutputSchema
)

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ml_features_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> GetMLFeatures:
    """Factory para o caso de uso GetMLFeatures."""
    return GetMLFeatures(repository)


def get_training_data_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> GetTrainingData:
    """Factory para o caso de uso GetTrainingData."""
    return GetTrainingData(repository)


def run_prediction_use_case() -> RunPrediction:
    """Factory para o caso de uso RunPrediction."""
    # Este caso de uso não depende de repositórios, por enquanto
    return RunPrediction()


@router.get(
    "/v1/ml/features",
    response_model=List[BookFeatureSchema],
    summary="Obter features de livros",
    description="Retorna a lista de livros formatados como vetores de "
                "features para inferência.",
    tags=["Machine Learning"],
    responses={
        200: {"description": "Features geradas com sucesso"},
        500: {"description": "Erro interno ao gerar features"}
    }
)
def get_ml_features(
    use_case: GetMLFeatures = Depends(get_ml_features_use_case)
):
    try:
        return use_case.execute()
    except Exception as e:
        logger.error(f"Erro ao gerar features: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar features."
        )


@router.get(
    "/v1/ml/training-data",
    response_model=List[TrainingDataSchema],
    summary="Obter dataset de treinamento",
    description="Retorna o dataset completo com features e target para "
                "treinamento de modelos.",
    tags=["Machine Learning"],
    responses={
        200: {"description": "Dataset gerado com sucesso"},
        500: {"description": "Erro ao gerar dataset de treinamento"}
    }
)
def get_training_data(
    use_case: GetTrainingData = Depends(get_training_data_use_case)
):
    try:
        return use_case.execute()
    except Exception as e:
        logger.error(
            f"Erro ao gerar dataset de treinamento: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar dataset de treinamento."
        )


@router.post(
    "/v1/ml/predictions",
    response_model=PredictionOutputSchema,
    summary="Executar predição de rating",
    description="Recebe os dados de um livro e retorna uma predição de "
                "rating (1-5) usando modelo de ML.",
    tags=["Machine Learning"],
    responses={
        200: {"description": "Predição executada com sucesso"},
        500: {"description": "Erro ao executar predição"}
    }
)
def run_prediction(
    input_data: PredictionInputSchema,
    use_case: RunPrediction = Depends(run_prediction_use_case)
):
    try:
        return use_case.execute(input_data)
    except Exception as e:
        logger.error(f"Erro ao executar predição: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao executar predição."
        )
