import logging
from typing import List
from src.domain.book import BookRepository
from src.app.schemas.ml_schema import BookFeatureSchema

class GetMLFeatures:
    """
    Caso de uso para obter todos os livros formatados como features de ML.
    """
    def __init__(self, repository: BookRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self) -> List[BookFeatureSchema]:
        self.logger.info("Iniciando busca de features de ML")
        books = self.repository.get_all_books()
        
        # Transforma os dados brutos em features
        features = []
        for book in books:
            features.append(BookFeatureSchema(
                id=book.id,
                price=book.price,
                avaliability=book.avaliability,
                category=book.category,
                title_length=len(book.title)  # Feature engineering simples
            ))
            
        self.logger.info(f"{len(features)} vetores de features gerados.")
        return features