import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os

BASE_URL = "https://books.toscrape.com/catalogue/"
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "books.csv")

def get_book_details(book_url: str) -> dict:
    """
    Extrai os detalhes de um único livro a partir de sua URL.

    Args:
        book_url: A URL completa da página do livro.

    Returns:
        Um dicionário contendo os detalhes do livro ou None em caso de erro.
    """
    try:
        response = requests.get(book_url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, "html.parser")

        # Extração dos dados
        title = soup.find("h1").text
        price = soup.find("p", class_="price_color").text
        
        # O rating é texto (e.g., "Three"), então convertemos para número
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_text = soup.find("p", class_="star-rating")["class"][1]
        rating = rating_map.get(rating_text, 0)
        
        availability_text = soup.find("p", class_="instock availability").text.strip()
        availability = " ".join(availability_text.split()) # Limpa espaços extras

        # A categoria está no breadcrumb
        category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
        
        # A URL da imagem é relativa, então a tornamos absoluta
        image_relative_url = soup.find("div", id="product_gallery").find("img")["src"]
        image_url = urljoin(book_url, image_relative_url)

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": category,
            "image_url": image_url,
            "book_url": book_url
        }

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL do livro {book_url}: {e}")
        return None
    except (AttributeError, KeyError) as e:
        print(f"Erro ao parsear os detalhes do livro {book_url}: {e}")
        return None

def scrape_all_books():
    """
    Função principal que navega por todas as páginas do site
    e extrai os dados de todos os livros.
    """
    all_books_data = []
    current_url = urljoin(BASE_URL, "page-1.html")
    page_num = 1

    while current_url:
        print(f"Coletando dados da página: {page_num}...")
        
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Encontra todos os links de livros na página atual
            books_on_page = soup.find_all("article", class_="product_pod")
            for book in books_on_page:
                book_relative_url = book.find("h3").find("a")["href"]
                book_full_url = urljoin(BASE_URL, book_relative_url)
                
                book_details = get_book_details(book_full_url)
                if book_details:
                    all_books_data.append(book_details)

            # Procura pelo botão "next" para ir para a próxima página
            next_page_element = soup.find("li", class_="next")
            if next_page_element:
                next_page_relative_url = next_page_element.find("a")["href"]
                current_url = urljoin(BASE_URL, next_page_relative_url)
                page_num += 1
            else:
                current_url = None 
        
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página de listagem {current_url}: {e}")
            current_url = None 

    return all_books_data


if __name__ == "__main__":
    """
    Ponto de entrada do script. Quando executado diretamente,
    inicia o processo de scraping e salva os resultados em um arquivo CSV.
    """
    print("Iniciando o processo de Web Scraping...")
    
    scraped_data = scrape_all_books()

    if scraped_data:
        print(f"\nScraping finalizado. Total de {len(scraped_data)} livros encontrados.")
        
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
            print(f"Diretório '{OUTPUT_FOLDER}' criado.")

        df = pd.DataFrame(scraped_data)
        
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        
        print(f"Dados salvos com sucesso em: '{OUTPUT_FILE}'")
    else:
        print("Nenhum dado foi coletado. Verifique os logs de erro.")