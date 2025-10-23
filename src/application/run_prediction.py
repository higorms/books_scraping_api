import logging
from src.app.schemas.ml_schema import PredictionInputSchema, PredictionOutputSchema

class RunPrediction:
    """
    Caso de uso para executar uma predição usando um modelo 'dummy'.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Caso de uso de predição inicializado (com modelo dummy).")

    def execute(self, input_data: PredictionInputSchema) -> PredictionOutputSchema:
        self.logger.info(f"Executando predição para: {input_data.title}")
        
        # 1. Feature Engineering 
        title_length = len(input_data.title)
        
        # 2. Lógica de predição (dummy)
        # Começa com rating 3
        predicted_rating = 3.0
        # Livros mais caros têm rating maior
        predicted_rating += (input_data.price * 0.05)
        # Livros com título mais longo têm rating maior
        predicted_rating += (title_length * 0.01)
        # Mais disponibilidade, menor o rating (raridade)
        predicted_rating -= (input_data.avaliability * 0.01)
        
        # Garante que o rating fique entre 1 e 5
        predicted_rating = max(1.0, min(5.0, predicted_rating))
        
        self.logger.info(f"Rating previsto: {predicted_rating:.2f}")
        
        return PredictionOutputSchema(predicted_rating=round(predicted_rating, 2))