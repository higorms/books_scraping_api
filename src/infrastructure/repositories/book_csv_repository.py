import csv
import logging
import pandas as pd
from typing import List, Optional
from src.domain.book import Book, BookRepository
from src.domain.exceptions import BookRepositoryException


class BookRepository(BookRepository):
    """Implementação do repositório de livros usando arquivo CSV.

    Esta classe implementa o protocolo BookRepository para persistência
    de dados de livros utilizando arquivos CSV como fonte de dados.

    Attributes:
        file_path (str): Caminho para o arquivo CSV contendo os dados
            dos livros.
    """

    def __init__(self, file_path: str):
        """Inicializa o repositório CSV com o caminho do arquivo.

        Args:
            file_path (str): Caminho para o arquivo CSV contendo os dados
                dos livros.
        """
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def get_all_books(self) -> List[Book]:
        """Recupera todos os livros do arquivo CSV.

        Lê o arquivo CSV especificado no construtor e converte cada linha
        em uma instância da classe Book.

        Returns:
            List[Book]: Lista contendo todos os livros encontrados no
                arquivo CSV.

        Raises:
            BookRepositoryException: Se houver problemas de acesso ao arquivo
                ou configuração.
            DataValidationError: Se algum valor no CSV não puder ser
                convertido para o tipo esperado.
        """
        books = []
        try:
            with open(self.file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        book = Book(
                            id=int(row["id"]),
                            title=row["title"],
                            price=float(row["price"]),
                            rating=int(row["rating"]),
                            avaliability=int(row["avaliability"]),
                            category=row["category"],
                            image_url=row["image_url"]
                        )
                        books.append(book)
                    except (ValueError, KeyError) as e:
                        error_msg = (
                            f"Erro ao processar linha {row_num} do CSV: {e}. "
                            f"Pulando registro."
                        )
                        self.logger.warning(error_msg)
                        # Continuamos processando outros registros
                        continue
                    except Exception as e:
                        error_msg = (
                            f"Erro inesperado ao processar linha "
                            f"{row_num}: {e}"
                        )
                        self.logger.error(error_msg)
                        continue
        except FileNotFoundError:
            error_msg = f"Arquivo CSV não encontrado: {self.file_path}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Arquivo de dados não encontrado: {self.file_path}",
                "FILE_NOT_FOUND"
            )
        except PermissionError:
            error_msg = f"Sem permissão para ler arquivo: {self.file_path}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Sem permissão para acessar arquivo: {self.file_path}",
                "PERMISSION_DENIED"
            )
        except Exception as e:
            error_msg = f"Erro inesperado ao ler arquivo CSV: {e}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Erro ao carregar dados dos livros: {e}",
                "UNEXPECTED_ERROR"
            )

        return books

    def search_books(self, title: str = "", category: str = "") -> List[Book]:
        """Busca livros com base em título e categoria.

        Lê o arquivo CSV especificado no construtor e filtra os livros
        que correspondem aos critérios de busca fornecidos.

        Args:
            title (str): Título ou parte do título do livro a ser buscado.
                Busca é case-insensitive. Padrão é string vazia, que não
                filtra por título.
            category (str): Categoria do livro a ser buscado. Busca é
                case-insensitive. Padrão é string vazia, que não filtra
                por categoria.

        Returns:
            List[Book]: Lista contendo os livros que correspondem aos
                critérios de busca.

        Raises:
            BookRepositoryException: Se houver problemas de acesso ao arquivo
                ou configuração.
            DataValidationError: Se algum valor no CSV não puder ser
                convertido para o tipo esperado.
        """

        try:
            df = pd.read_csv(self.file_path)

            if title:
                df = df[df['title'].str.contains(title,
                                                 case=False,
                                                 na=False)]
            if category:
                df = df[df['category'].str.contains(category,
                                                    case=False,
                                                    na=False)]

            # Converter DataFrame para lista de objetos Book
            books = []
            for _, row in df.iterrows():
                try:
                    book = Book(
                        id=int(row["id"]),
                        title=row["title"],
                        price=float(row["price"]),
                        rating=int(row["rating"]),
                        avaliability=int(row["avaliability"]),
                        category=row["category"],
                        image_url=row["image_url"]
                    )
                    books.append(book)
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Erro ao processar registro: {e}")
                    continue

            return books

        except FileNotFoundError:
            error_msg = f"Arquivo CSV não encontrado: {self.file_path}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Arquivo de dados não encontrado: {self.file_path}",
                "FILE_NOT_FOUND"
            )
        except PermissionError:
            error_msg = f"Sem permissão para ler arquivo: {self.file_path}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Sem permissão para acessar arquivo: {self.file_path}",
                "PERMISSION_DENIED"
            )
        except Exception as e:
            error_msg = f"Erro inesperado ao ler arquivo CSV: {e}"
            self.logger.error(error_msg)
            raise BookRepositoryException(
                f"Erro ao carregar dados dos livros: {e}",
                "UNEXPECTED_ERROR"
            )

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Recupera um único livro pelo seu ID."""
        try:
            df = pd.read_csv(self.file_path)
            book_data = df[df['id'] == book_id]
            
            if not book_data.empty:
                # Converte a primeira linha encontrada para um objeto Book
                return Book(**book_data.iloc[0].to_dict())
            
            # Retorna None se nenhum livro for encontrado com o ID
            return None
        except FileNotFoundError:
            raise BookRepositoryException(f"Arquivo de dados não encontrado: {self.file_path}", "FILE_NOT_FOUND")
        except Exception as e:
            raise BookRepositoryException(f"Erro ao buscar livro por ID: {e}", "UNEXPECTED_ERROR")

    def get_all_categories(self) -> List[str]:
        """Recupera uma lista de todas as categorias de livros únicas."""
        try:
            df = pd.read_csv(self.file_path)
            
            if 'category' in df.columns:
                # Pega todas as categorias, remove as duplicadas e ordena
                unique_categories = df['category'].unique()
                return sorted(list(unique_categories))
            
            # Retorna lista vazia se a coluna 'category' não existir
            return []
        except FileNotFoundError:
            raise BookRepositoryException(f"Arquivo de dados não encontrado: {self.file_path}", "FILE_NOT_FOUND")
        except Exception as e:
            raise BookRepositoryException(f"Erro ao buscar categorias: {e}", "UNEXPECTED_ERROR")
            