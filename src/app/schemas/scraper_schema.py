from pydantic import BaseModel


class ScraperResponseSchema(BaseModel):
    """Schema para a resposta da execução do scraper.

    Este schema define a estrutura de dados retornada pela API
    quando o scraper é executado.

    Attributes:
        success (bool): Indica se a execução foi bem-sucedida.
        message (str): Mensagem descritiva sobre a execução.
        books_count (int): Número de livros coletados pelo scraper.
        file_path (str | None): Caminho do arquivo onde os dados foram salvos,
            ou None se não houve salvamento.
    """
    success: bool
    message: str
    books_count: int
    file_path: str | None
