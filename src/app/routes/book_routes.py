import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.application.get_all_books import GetAllBooks
from src.application.search_books import SearchBooks
from src.application.get_book_by_id import GetBookById
from src.application.get_all_categories import GetAllCategories
from src.application.scraper import RunScraper
from src.infrastructure.repositories.book_csv_repository import (
    BookRepository as BookCSVRepository
)
from src.domain.book import BookRepository
from src.domain.exceptions import (
    BookRepositoryException,
    BookNotFoundError
)
from src.app.schemas.book_schema import BookSchema
from src.application.get_book_recommendations import FindSimilarBooksByText
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.repositories.pinecone_repository import (
    PineconeRepository
)
from src.app.schemas.scraper_schema import ScraperResponseSchema
from src.app.middleware.auth_middleware import require_auth

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


def get_pinecone_repository() -> PineconeRepository:
    """Factory para o repositório Pinecone."""
    try:
        return PineconeRepository()
    except Exception as e:
        logger.error(f"Erro ao instanciar o repositório Pinecone: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de busca por similaridade está indisponível."
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


def run_scraper_use_case() -> RunScraper:
    """Factory para o caso de uso RunScraper."""
    return RunScraper()


def get_embedding_service() -> EmbeddingService:
    """Factory para o serviço de embedding."""
    return EmbeddingService()


def find_similar_books_use_case(
    pinecone_repo: PineconeRepository = Depends(get_pinecone_repository),
    csv_repo: BookCSVRepository = Depends(get_book_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> FindSimilarBooksByText:
    """Factory para o caso de uso FindSimilarBooksByText."""
    if not pinecone_repo:
        raise HTTPException(
            status_code=503,
            detail="Serviço de busca indisponível."
        )
    return FindSimilarBooksByText(pinecone_repo, csv_repo, embedding_service)


@router.get(
    "/v1/books",
    response_model=List[BookSchema],
    summary="Listar todos os livros",
    description="Retorna a lista completa de livros disponíveis no catálogo.",
    tags=["Livros"],
    responses={
        200: {"description": "Lista de livros retornada com sucesso"},
        404: {"description": "Nenhum livro encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)
def get_books(use_case: GetAllBooks = Depends(get_use_case)):
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
    description="Busca livros por título e/ou categoria.",
    tags=["Livros"],
    responses={
        200: {"description": "Livros encontrados com sucesso"},
        404: {
            "description": (
                "Nenhum livro encontrado com os critérios fornecidos"
            )
        },
        500: {"description": "Erro interno do servidor"}
    }
)
def search_books(
    title: str = "",
    category: str = "",
    use_case: SearchBooks = Depends(search_books_use_case)
):
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
    "/v1/books/recommendations",
    response_model=List[BookSchema],
    summary="Buscar livros por similaridade",
    description="Recebe um texto e retorna livros semanticamente similares.",
    tags=["Recomendações"],
    responses={
        200: {"description": "Recomendações encontradas com sucesso"},
        400: {"description": "Parâmetro de busca inválido"},
        500: {"description": "Erro ao processar a busca"}
    }
)
def find_similar_books(
    query: str,
    use_case: FindSimilarBooksByText = Depends(find_similar_books_use_case)
):
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O parâmetro 'query' não pode ser vazio."
        )

    try:
        recommendations = use_case.execute(query_text=query)
        return [book.__dict__ for book in recommendations]
    except Exception as e:
        logger.error(f"Erro ao processar busca por similaridade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a busca."
        )


@router.get(
    "/v1/books/{id}",
    response_model=BookSchema,
    summary="Obter um livro por ID",
    description="Busca um livro específico pelo seu identificador único.",
    tags=["Livros"],
    responses={
        200: {"description": "Livro encontrado com sucesso"},
        404: {"description": "Livro não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)
def get_book_by_id(
    id: int,
    use_case: GetBookById = Depends(get_book_by_id_use_case)
):
    try:
        book = use_case.execute(book_id=id)
        return book.__dict__
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
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
    summary="Listar todas as categorias",
    description="Retorna a lista de todas as categorias únicas disponíveis.",
    tags=["Categorias"],
    responses={
        200: {"description": "Lista de categorias retornada com sucesso"},
        404: {"description": "Nenhuma categoria encontrada"},
        500: {"description": "Erro interno do servidor"}
    }
)
def get_all_categories(
    use_case: GetAllCategories = Depends(get_all_categories_use_case)
):
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


@router.post(
    "/v1/scraper/run",
    response_model=ScraperResponseSchema,
    summary="Executar o scraper de livros",
    description="Executa o web scraper para coletar dados de livros do site "
                "books.toscrape.com e salva os resultados em um arquivo CSV. "
                "**Requer autenticação JWT.**",
    tags=["Scraper"],
    dependencies=[Depends(require_auth)],
    responses={
        200: {"description": "Scraper executado com sucesso"},
        401: {"description": "Token JWT inválido ou ausente"},
        500: {"description": "Erro ao executar o scraper"}
    }
)
def run_scraper(
    use_case: RunScraper = Depends(run_scraper_use_case)
):
    try:
        logger.info("Recebida requisição para executar o scraper")
        result = use_case.execute()
        logger.info(f"Scraper executado: {result['message']}")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar o scraper: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar o scraper: {str(e)}"
        )
