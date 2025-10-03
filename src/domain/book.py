from dataclasses import dataclass
from typing import Protocol, List, Optional


@dataclass
class Book:
    """Classe que representa um livro.

    Attributes:
        id (int): Identificador único do livro.
        title (str): Título do livro.
        price (float): Preço do livro em formato decimal.
        rating (int): Avaliação do livro (1-5 estrelas).
        avaliability (int): Quantidade disponível em estoque.
        category (str): Categoria do livro.
        image_url (str): URL da imagem de capa do livro.
    """
    id: int
    title: str
    price: float
    rating: int
    avaliability: int
    category: str
    image_url: str


class BookRepository(Protocol):
    """Protocolo que define a interface para repositórios de livros.

    Este protocolo especifica os métodos que devem ser implementados
    por qualquer repositório de livros na aplicação.
    """

    def get_all_books(self) -> List[Book]:
        """Recupera todos os livros do repositório.

        Returns:
            List[Book]: Lista contendo todos os livros disponíveis.
        """
        ...

    def search_books(self, title: str, category: str) -> List[Book]:
        """Busca livros no repositório com base em título e categoria.

        Args:
            title (str): Título ou parte do título do livro a ser buscado.
            category (str): Categoria do livro a ser buscado.

        Returns:
            List[Book]: Lista contendo os livros que correspondem aos
                critérios de busca.
        """
        ...

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Recupera um único livro pelo seu ID.

        Args:
            book_id (int): O ID do livro a ser buscado.

        Returns:
            Optional[Book]: O objeto Book se encontrado, caso contrário None.
        """
        ...

    def get_all_categories(self) -> List[str]:
        """Recupera uma lista de todas as categorias de livros únicas.

        Returns:
            List[str]: Lista contendo os nomes das categorias.
        """
        ...