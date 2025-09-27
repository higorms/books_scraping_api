import logging
from typing import List
from src.domain.book import Book, BookRepository
from src.domain.exceptions import (
    BookRepositoryException,
    BookNotFoundError
)


class SearchBooks:
    """Caso de uso para buscar livros por título e categoria.

    Esta classe implementa a lógica de negócio para buscar livros
    disponíveis no sistema, utilizando o padrão Repository para
    abstração da camada de dados.

    Attributes:
        repository (BookRepository): Instância do repositório de livros.
    """

    def __init__(self, repository: BookRepository):
        """Inicializa o caso de uso com o repositório fornecido.

        Args:
            repository (BookRepository): Implementação do repositório
                de livros.
        """
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    def execute(self, title: str = "", category: str = "") -> List[Book]:
        """Executa o caso de uso para buscar os livros
        com os parâmetros de busca.

        Returns:
            List[Book]: Lista contendo todos os livros
            compatíveis com a busca no repositório.

        Raises:
            BookRepositoryException: Quando há problemas de acesso aos dados.
            BookNotFoundError: Quando nenhum livro é encontrado.
        """
        try:
            self.logger.info(f"Iniciando busca - "
                             f"título: '{title}', "
                             f"categoria: '{category}'")
            books = self.repository.search_books(
                title,
                category
                )

            if not books:
                self.logger.warning("Nenhum livro encontrado no repositório")
                raise BookNotFoundError(
                    "Nenhum livro encontrado no catálogo",
                    "NO_BOOKS_FOUND"
                )

            self.logger.info(
                f"Busca concluída. {len(books)} livros encontrados"
            )
            return books

        except BookRepositoryException:
            # Re-propaga exceções do repositório
            raise
        except BookNotFoundError:
            # Re-propaga exceções de livros não encontrados
            raise
        except Exception as e:
            error_msg = f"Erro inesperado ao buscar livros: {e}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Falha ao recuperar lista de livros: {e}",
                "UNEXPECTED_ERROR"
            )
