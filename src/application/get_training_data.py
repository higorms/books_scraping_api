import logging
from typing import List
from src.domain.book import BookRepository
from src.app.schemas.ml_schema import TrainingDataSchema

class GetTrainingData:
    """
    Caso de uso para obter o dataset de treinamento (features + target).
    """
    def __init__(self, repository: BookRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self) -> List[TrainingDataSchema]:
        self.logger.info("Iniciando geração do dataset de treinamento")
        books = self.repository.get_all_books()
        
        # Formata os dados para treinamento
        training_set = []
        for book in books:
            training_set.append(TrainingDataSchema(
                price=book.price,
                avaliability=book.avaliability,
                title_length=len(book.title),
                rating=book.rating  # Inclui o target
            ))
            
        self.logger.info(f"{len(training_set)} registros de treinamento gerados.")
        return training_set