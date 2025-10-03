import logging
from typing import List
from src.domain.book import Book, BookRepository
from src.domain.exceptions import (
    BookRepositoryException,
    BookNotFoundError
)


class GetAllBooks:
    """Caso de uso para recuperar todos os livros.

    Esta classe implementa a lógica de negócio para obter todos os livros
    disponíveis no sistema, utilizando o padrão Repository para abstração
    da camada de dados.

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

    def execute(self) -> List[Book]:
        """Executa o caso de uso para obter todos os livros.

        Returns:
            List[Book]: Lista contendo todos os livros disponíveis no
                repositório.

        Raises:
            BookRepositoryException: Quando há problemas de acesso aos dados.
            BookNotFoundError: Quando nenhum livro é encontrado.
        """
        try:
            self.logger.info("Iniciando busca de todos os livros")
            books = self.repository.get_all_books()

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
