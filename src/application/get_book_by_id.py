import logging
from typing import Optional
from src.domain.book import Book, BookRepository
from src.domain.exceptions import BookNotFoundError

class GetBookById:
    """Caso de uso para recuperar um livro pelo seu ID."""
    def __init__(self, repository: BookRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self, book_id: int) -> Optional[Book]:
        self.logger.info(f"Iniciando busca pelo livro com ID: {book_id}")
        book = self.repository.get_book_by_id(book_id)
        if not book:
            self.logger.warning(f"Livro com ID {book_id} não encontrado.")
            raise BookNotFoundError(f"Livro com ID {book_id} não encontrado.", "BOOK_NOT_FOUND")
        
        self.logger.info(f"Livro com ID {book_id} encontrado: '{book.title}'")
        return book