import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import re
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


class RunScraper:
    """Caso de uso para executar o scraper de livros.

    Este caso de uso encapsula a lógica de execução do scraper,
    seguindo os princípios de Clean Architecture.
    """

    BASE_URL = "https://books.toscrape.com/catalogue/"

    def __init__(self):
        """Inicializa o caso de uso."""
        self.output_folder = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data'
        )
        self.output_file = os.path.join(self.output_folder, "books.csv")

    def execute(self) -> Dict[str, any]:
        """Executa o scraper e salva os resultados.

        Returns:
            Dict contendo informações sobre a execução do scraper:
                - success (bool): Se a execução foi bem-sucedida
                - message (str): Mensagem descritiva
                - books_count (int): Número de livros coletados
                - file_path (str): Caminho do arquivo salvo

        Raises:
            Exception: Se houver erro durante a execução do scraper
        """
        try:
            logger.info("Iniciando processo de scraping...")

            # Executa o scraper
            scraped_data = self._scrape_all_books()

            if not scraped_data:
                logger.warning("Nenhum dado foi coletado pelo scraper")
                return {
                    "success": False,
                    "message": "Nenhum dado foi coletado. "
                               "Verifique a conexão com o site.",
                    "books_count": 0,
                    "file_path": None
                }

            # Cria o diretório se não existir
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
                logger.info(f"Diretório '{self.output_folder}' criado.")

            # Prepara os dados
            df = pd.DataFrame(scraped_data)
            df['id'] = df.index + 1

            # Reorganiza as colunas conforme o schema
            schema_columns = [
                'id', 'title', 'price', 'rating', 'avaliability',
                'category', 'image_url'
            ]
            df = df[schema_columns]

            # Salva os dados
            df.to_csv(self.output_file, index=False, encoding='utf-8')

            books_count = len(scraped_data)
            logger.info(
                f"Scraping finalizado com sucesso. "
                f"Total de {books_count} livros coletados."
            )

            return {
                "success": True,
                "message": f"Scraping concluído com sucesso. "
                           f"{books_count} livros foram coletados e salvos.",
                "books_count": books_count,
                "file_path": self.output_file
            }

        except Exception as e:
            logger.error(f"Erro durante a execução do scraper: {e}")
            raise Exception(f"Erro ao executar o scraper: {str(e)}")

    def _get_book_details(self, book_url: str) -> Optional[dict]:
        """
        Extrai e limpa os detalhes de um único livro a partir de sua URL,
        alinhando os tipos de dados com o BookSchema.

        Args:
            book_url: A URL completa da página do livro.

        Returns:
            Um dicionário contendo os detalhes do livro ou None em caso
            de erro.
        """
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("h1").text

            price_text = soup.find("p", class_="price_color").text
            price = float(price_text.replace('£', '').strip())

            rating_map = {
                "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
            }
            rating_text = soup.find("p", class_="star-rating")["class"][1]
            rating = rating_map.get(rating_text, 0)

            availability_text = soup.find(
                "p", class_="instock availability"
            ).text.strip()
            match = re.search(r'\((\d+) available\)', availability_text)
            avaliability = int(match.group(1)) if match else 0

            category = soup.find(
                "ul", class_="breadcrumb"
            ).find_all("a")[2].text

            image_relative_url = soup.find(
                "div", id="product_gallery"
            ).find("img")["src"]
            image_url = urljoin(book_url, image_relative_url)

            return {
                "title": title,
                "price": price,
                "rating": rating,
                "avaliability": avaliability,
                "category": category,
                "image_url": image_url,
            }

        except requests.exceptions.RequestException as e:
            logger.warning(f"Erro ao acessar a URL do livro {book_url}: {e}")
            return None
        except (AttributeError, KeyError, ValueError) as e:
            logger.warning(
                f"Erro ao parsear os detalhes do livro {book_url}: {e}"
            )
            return None

    def _scrape_all_books(self) -> List[dict]:
        """
        Função principal que navega por todas as páginas do site
        e extrai os dados de todos os livros.

        Returns:
            Lista de dicionários contendo os dados dos livros coletados.
        """
        all_books_data = []
        current_url = urljoin(self.BASE_URL, "page-1.html")
        page_num = 1

        while current_url:
            logger.info(f"Coletando dados da página: {page_num}...")

            try:
                response = requests.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                books_on_page = soup.find_all("article", class_="product_pod")
                for book in books_on_page:
                    book_relative_url = book.find("h3").find("a")["href"]
                    book_full_url = urljoin(self.BASE_URL, book_relative_url)

                    book_details = self._get_book_details(book_full_url)
                    if book_details:
                        all_books_data.append(book_details)

                next_page_element = soup.find("li", class_="next")
                if next_page_element:
                    next_page_relative_url = next_page_element.find(
                        "a"
                    )["href"]
                    current_url = urljoin(
                        self.BASE_URL, next_page_relative_url
                    )
                    page_num += 1
                else:
                    current_url = None

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Erro ao acessar a página de listagem {current_url}: {e}"
                )
                current_url = None

        return all_books_data


if __name__ == "__main__":
    """
    Ponto de entrada do script. Quando executado diretamente,
    inicia o processo de scraping e salva os resultados em um arquivo CSV.
    """
    print("Iniciando o processo de Web Scraping...")

    scraper = RunScraper()
    result = scraper.execute()

    if result["success"]:
        print(f"\n{result['message']}")
        print(f"Arquivo salvo em: '{result['file_path']}'")
    else:
        print(f"\n{result['message']}")
