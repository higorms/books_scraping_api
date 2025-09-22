from typing import List
from src.domain.book import Book, BookRepository


class GetAllBooks:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def execute(self) -> List[Book]:
        return self.repository.get_all_books()
