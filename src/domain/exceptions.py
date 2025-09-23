"""Exceções customizadas da aplicação Books Scraping API.

Este módulo define exceções específicas do domínio da aplicação,
proporcionando melhor tratamento e categorização de erros.
"""


class BookScrapingAPIException(Exception):
    """Exceção base para a aplicação Books Scraping API.

    Todas as exceções específicas da aplicação devem herdar desta classe.

    Attributes:
        message (str): Mensagem descritiva do erro.
        error_code (str): Código único do erro para facilitar debugging.
    """

    def __init__(self, message: str, error_code: str = None):
        """Inicializa a exceção com mensagem e código de erro.

        Args:
            message (str): Mensagem descritiva do erro.
            error_code (str): Código único do erro (opcional).
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class BookRepositoryException(BookScrapingAPIException):
    """exceção para erros relacionados ao repositório de livros.

    Lançada quando há problemas de acesso aos dados dos livros,
    seja por questões de arquivo, permissões ou formato de dados.
    """
    pass


class BookNotFoundError(BookScrapingAPIException):
    """exceção para quando nenhum livro é encontrado.

    Lançada quando uma busca por livros não retorna resultados.
    """
    pass


class DataValidationError(BookScrapingAPIException):
    """exceção para erros de validação de dados.

    Lançada quando os dados dos livros não estão no formato esperado
    ou contém valores inválidos.
    """
    pass


class ConfigurationError(BookScrapingAPIException):
    """exceção para erros de configuração da aplicação.

    Lançada quando há problemas na configuração de dependências
    ou inicialização da aplicação.
    """
    pass
