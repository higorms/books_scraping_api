import logging
from fastapi import APIRouter, Depends, status
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
    summary="Obter dados formatados como features",
    tags=["Machine Learning"]
)
def get_ml_features(
    use_case: GetMLFeatures = Depends(get_ml_features_use_case)
):
    """
    Retorna a lista completa de livros formatados como vetores 
    de features para inferência (sem a variável target).
    """
    try:
        return use_case.execute()
    except Exception as e:
        logger.error(f"Erro ao gerar features: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao gerar features.")

@router.get(
    "/v1/ml/training-data",
    response_model=List[TrainingDataSchema],
    summary="Obter dataset de treinamento",
    tags=["Machine Learning"]
)
def get_training_data(
    use_case: GetTrainingData = Depends(get_training_data_use_case)
):
    """
    Retorna o dataset completo (features + target) 
    para treinamento de modelos.
    """
    try:
        return use_case.execute()
    except Exception as e:
        logger.error(f"Erro ao gerar dataset de treinamento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao gerar dataset de treinamento.")

@router.post(
    "/v1/ml/predictions",
    response_model=PredictionOutputSchema,
    summary="Executar uma predição de rating",
    tags=["Machine Learning"]
)
def run_prediction(
    input_data: PredictionInputSchema,
    use_case: RunPrediction = Depends(run_prediction_use_case)
):
    """
    Recebe os dados de um livro (título, preço, disponibilidade) 
    e retorna uma predição de rating (1-5).
    Utiliza um modelo dummy para fins de demonstração.
    """
    try:
        return use_case.execute(input_data)
    except Exception as e:
        logger.error(f"Erro ao executar predição: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao executar predição.")
