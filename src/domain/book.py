from dataclasses import dataclass
from typing import Protocol, List


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
