from dataclasses import dataclass
from typing import Protocol, List


@dataclass
class Book:
    id: int
    title: str
    price: float
    rating: float
    avaliability: bool
    category: str
    image: str


class BookRepository(Protocol):
    def get_all_books(self) -> List[Book]:
        ...
