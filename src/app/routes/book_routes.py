import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.application.get_all_books import GetAllBooks
from src.application.search_books import SearchBooks
from src.application.get_book_by_id import GetBookById
from src.application.get_all_categories import GetAllCategories
from src.infrastructure.repositories.book_csv_repository import (
    BookRepository as BookCSVRepository
)
from src.domain.book import BookRepository
from src.domain.exceptions import (
    BookRepositoryException,
    BookNotFoundError
)
from src.app.schemas.book_schema import BookSchema

router = APIRouter()
logger = logging.getLogger(__name__)


def get_book_repository() -> BookRepository:
    """Factory para o repositório de livros."""
    try:
        return BookCSVRepository("data/books.csv")
    except Exception as e:
        logger.error(f"Erro ao instanciar o repositório: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao acessar a fonte de dados"
        )


def get_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> GetAllBooks:
    """Factory para o caso de uso GetAllBooks,
    que depende de um repositório."""
    return GetAllBooks(repository)


def search_books_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> SearchBooks:
    """Factory para o caso de uso SearchBooks,
    que depende de um repositório."""
    return SearchBooks(repository)


def get_book_by_id_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> GetBookById:
    """Factory para o caso de uso GetBookById,
    que depende de um repositório."""
    return GetBookById(repository)


def get_all_categories_use_case(
    repository: BookRepository = Depends(get_book_repository)
) -> GetAllCategories:
    """Factory para o caso de uso GetAllCategories,
    que depende de um repositório."""
    return GetAllCategories(repository)


@router.get(
    "/v1/books",
    response_model=List[BookSchema],
    summary="Obter todos os livros",
    tags=["Livros"],
)
def get_books(use_case: GetAllBooks = Depends(get_use_case)):
    """Endpoint para recuperar todos os livros disponíveis."""
    try:
        logger.info("Processando requisição para obter todos os livros")
        books = use_case.execute()
        logger.info(f"Retornando {len(books)} livros encontrados")
        return [book.__dict__ for book in books]
    except BookNotFoundError as e:
        logger.warning(f"Nenhum livro encontrado: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except BookRepositoryException as e:
        logger.error(
            f"Erro do repositório ao buscar todos os livros: {e.message}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao acessar os dados dos livros."
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao processar requisição: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/v1/books/search",
    response_model=List[BookSchema],
    summary="Buscar livros",
    tags=["Livros"],
)
def search_books(
    title: str = "",
    category: str = "",
    use_case: SearchBooks = Depends(search_books_use_case)
):
    """Endpoint para buscar livros com base em critérios."""
    try:
        logger.info("Processando requisição para buscar livros")
        books = use_case.execute(title, category)
        logger.info(f"Retornando {len(books)} livros encontrados")
        return [book.__dict__ for book in books]
    except BookNotFoundError as e:
        logger.warning(f"Nenhum livro encontrado na busca: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except BookRepositoryException as e:
        logger.error(f"Erro do repositório na busca: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao acessar os dados dos livros."
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao processar busca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/v1/books/{id}",
    response_model=BookSchema,
    summary="Obter um livro por ID",
    tags=["Livros"]
)
def get_book_by_id(
    id: int,
    use_case: GetBookById = Depends(get_book_by_id_use_case)
):
    """Endpoint para buscar um livro específico pelo seu ID."""
    try:
        book = use_case.execute(book_id=id)
        return book.__dict__
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
            )
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar livro por ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
            )


@router.get(
    "/v1/categories",
    response_model=List[str],
    summary="Listar todas as categorias de livros",
    tags=["Categorias"]
)
def get_all_categories(
    use_case: GetAllCategories = Depends(get_all_categories_use_case)
):
    """Endpoint para listar todas as categorias de livros únicas."""
    try:
        categories = use_case.execute()
        return categories
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
            )
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar categorias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
