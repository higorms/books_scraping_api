import csv
from typing import List
from src.domain.book import Book, BookRepository


class BookRepository(BookRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_books(self) -> List[Book]:
        books = []
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                books.append(Book(
                    id=int(row["id"]),
                    title=row["title"],
                    price=float(row["price"]),
                    rating=float(row["rating"]),
                    avaliability=row["avaliability"],
                    category=row["category"],
                    image=row["image"]
                ))
                return books
