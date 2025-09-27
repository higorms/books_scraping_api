import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.application.get_all_books import GetAllBooks
from src.application.search_books import SearchBooks
from src.application.get_book_by_id import GetBookById
from src.application.get_all_categories import GetAllCategories
from src.infrastructure.repositories.book_csv_repository import BookRepository
from src.app.schemas.book_schema import BookSchema
from src.domain.exceptions import (
    BookRepositoryException,
    BookNotFoundError
)


router = APIRouter()
logger = logging.getLogger(__name__)

def get_book_repository() -> BookRepository:
    """Factory para o repositório de livros."""
    try:
        return BookRepository("data/books.csv")
    except Exception as e:
        logger.error(f"Erro ao instanciar o repositório: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao acessar a fonte de dados"
        )

def get_use_case() -> GetAllBooks:
    """Factory function para criar instância do caso de uso GetAllBooks.

    Esta função configura e retorna uma instância do caso de uso GetAllBooks
    com suas dependências adequadamente injetadas.

    Returns:
        GetAllBooks: Instância configurada do caso de uso para obter
            todos os livros.

    Raises:
        HTTPException: Se houver erro na configuração das dependências.
    """
    try:
        repository = BookRepository("data/books.csv")
        return GetAllBooks(repository)
    except Exception as e:
        logger.error(f"Erro ao configurar dependências: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao configurar dependências"
        )


@router.get(
    "/v1/books",
    response_model=List[BookSchema],
    summary="Obter todos os livros",
    description="Retorna uma lista com todos os livros disponíveis no "
                "catálogo.",
    response_description="Lista de livros com informações detalhadas "
                         "incluindo título, preço, avaliação e "
                         "disponibilidade.",
    tags=["Livros"],
    responses={
        200: {
            "description": "Lista de livros recuperada com sucesso",
            "model": List[BookSchema]
        },
        404: {
            "description": "Nenhum livro encontrado ou arquivo de dados "
                           "não existe"
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
def get_books(use_case: GetAllBooks = Depends(get_use_case)):
    """Endpoint para recuperar todos os livros disponíveis.

    Esta rota retorna uma lista completa de todos os livros presentes
    no catálogo, incluindo informações como título, preço, avaliação,
    disponibilidade, categoria e URL da imagem.

    Args:
        use_case (GetAllBooks): Caso de uso injetado via dependency injection.

    Returns:
        List[BookSchema]: Lista de livros serializados conforme o schema
            definido.

    Raises:
        HTTPException: Em caso de erro interno do servidor ou dados
            não encontrados.
    """
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
        if "não encontrado" in e.message.lower():
            logger.error(f"Arquivo de dados não encontrado: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dados dos livros não encontrados"
            )
        elif "permissão" in e.message.lower():
            logger.error(f"Erro de permissão: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro de acesso aos dados do sistema"
            )
        else:
            logger.error(f"Erro do repositório: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor"
            )
    except HTTPException:
        # Re-raise HTTPExceptions para manter status codes específicos
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao processar requisição: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


def search_books_use_case() -> SearchBooks:
    """Factory function para criar instância do caso de uso SearchBooks.

    Esta função configura e retorna uma instância do caso de uso SearchBooks
    com suas dependências adequadamente injetadas.

    Returns:
        SearchBooks: Instância configurada do caso de uso para buscar
            livros.
    """
    try:
        repository = BookRepository("data/books.csv")
        return SearchBooks(repository)
    except Exception as e:
        logger.error(f"Erro ao configurar dependências: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao configurar dependências"
        )


@router.get(
    "/v1/books/search",
    response_model=List[BookSchema],
    summary="Buscar livros",
    description="Retorna uma lista de livros que correspondem "
    "aos critérios de busca.",
    response_description="Lista de livros que correspondem "
    "aos critérios de busca.",
    tags=["Livros"],
    responses={
        200: {
            "description": "Lista de livros recuperada com sucesso",
            "model": List[BookSchema]
        },
        404: {
            "description": "Nenhum livro encontrado ou arquivo de dados "
                           "não existe"
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
def search_books(
    title: str = "",
    category: str = "",
    use_case: SearchBooks = Depends(search_books_use_case)
):
    """Endpoint para buscar livros com base em critérios.

    Esta rota permite buscar livros no catálogo com base em parâmetros
    como título e categoria, retornando uma lista de livros que
    correspondem aos critérios fornecidos.

    Args:
        use_case (SearchBooks): Caso de uso injetado via dependency injection.

    Returns:
        List[BookSchema]: Lista de livros serializados conforme o schema
            definido.

    Raises:
        HTTPException: Em caso de erro interno do servidor ou dados
            não encontrados.
    """
    try:
        logger.info("Processando requisição para buscar livros")
        books = use_case.execute(title, category)

        logger.info(f"Retornando {len(books)} livros encontrados")
        return [book.__dict__ for book in books]

    except BookNotFoundError as e:
        logger.warning(f"Nenhum livro encontrado: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except BookRepositoryException as e:
        if "não encontrado" in e.message.lower():
            logger.error(f"Arquivo de dados não encontrado: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dados dos livros não encontrados"
            )
        elif "permissão" in e.message.lower():
            logger.error(f"Erro de permissão: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro de acesso aos dados do sistema"
            )
        else:
            logger.error(f"Erro do repositório: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor"
            )
    except HTTPException:
        # Re-raise HTTPExceptions para manter status codes específicos
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao processar requisição: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

def get_book_by_id_use_case(repository: BookRepository = Depends(get_book_repository)) -> GetBookById:
    return GetBookById(repository)

@router.get(
    "/v1/books/{id}",
    response_model=BookSchema,
    summary="Obter um livro por ID",
    tags=["Livros"]
)
def get_book_by_id(id: int, use_case: GetBookById = Depends(get_book_by_id_use_case)):
    try:
        book = use_case.execute(book_id=id)
        return book.__dict__
    except BookNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar livro por ID: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")

def get_all_categories_use_case(repository: BookRepository = Depends(get_book_repository)) -> GetAllCategories:
    return GetAllCategories(repository)

@router.get(
    "/v1/categories",
    response_model=List[str],
    summary="Listar todas as categorias de livros",
    tags=["Categorias"]
)
def get_all_categories(use_case: GetAllCategories = Depends(get_all_categories_use_case)):
    try:
        categories = use_case.execute()
        return categories
    except BookNotFoundError as e:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")
