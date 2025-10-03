from pydantic import BaseModel, ConfigDict


class BookSchema(BaseModel):
    """Schema Pydantic para serialização/deserialização de dados de livros.

    Este schema define a estrutura de dados para livros na API,
    garantindo validação automática dos tipos e conversão de dados.

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

    model_config = ConfigDict(from_attributes=True)
