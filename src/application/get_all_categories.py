import logging
from typing import List
from src.domain.book import BookRepository
from src.domain.exceptions import BookNotFoundError

class GetAllCategories:
    """Caso de uso para recuperar todas as categorias de livros."""
    def __init__(self, repository: BookRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self) -> List[str]:
        self.logger.info("Iniciando busca de todas as categorias.")
        categories = self.repository.get_all_categories()
        if not categories:
            self.logger.warning("Nenhuma categoria encontrada no repositório.")
            raise BookNotFoundError("Nenhuma categoria encontrada.", "NO_CATEGORIES_FOUND")
            
        self.logger.info(f"{len(categories)} categorias encontradas.")
        return categories