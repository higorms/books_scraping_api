from fastapi import APIRouter, Depends
from typing import List
from src.application.get_all_books import GetAllBooks
from src.infrastructure.repositories.book_csv_repository import BookRepository
from src.app.schemas.book_schema import BookSchema


router = APIRouter()


def get_use_case() -> GetAllBooks:
    repository = BookRepository("data/books.csv")
    return GetAllBooks(repository)


@router.get("/v1/books", response_model=List[BookSchema])
def get_books(use_case: GetAllBooks = Depends(get_use_case)):
    books = use_case.execute()
    return [book.__dict__ for book in books]
