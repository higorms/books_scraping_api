from pydantic import BaseModel
from typing import List

class BookFeatureSchema(BaseModel):
    """
    Schema para dados formatados como features para inferência.
    Exclui o 'target' (rating).
    """
    id: int
    price: float
    avaliability: int
    category: str
    title_length: int

class TrainingDataSchema(BaseModel):
    """
    Schema para o dataset de treinamento.
    Inclui as features e o 'target' (rating).
    """
    price: float
    avaliability: int
    title_length: int
    rating: int  # Nosso 'target' (variável a ser prevista)

class PredictionInputSchema(BaseModel):
    """
    Schema para os dados de entrada que o modelo espera.
    """
    title: str
    price: float
    avaliability: int

class PredictionOutputSchema(BaseModel):
    """
    Schema para a resposta da predição.
    """
    predicted_rating: float
