import logging
from src.infrastructure.repositories.book_csv_repository import BookRepository as BookCSVRepository
from src.infrastructure.repositories.pinecone_repository import PineconeRepository
from src.infrastructure.services.embedding_service import EmbeddingService
from tqdm import tqdm

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_indexing():
    """
    Script para ler livros do CSV, gerar embeddings e indexá-los no Pinecone.
    """
    logger = logging.getLogger(__name__)
    logger.info("Iniciando processo de indexação de livros...")

    try:
        # 1. Inicializar os repositórios e serviços
        csv_repo = BookCSVRepository("data/books.csv")
        pinecone_repo = PineconeRepository()
        embedding_service = EmbeddingService()

        # 2. Carregar todos os livros do CSV
        books = csv_repo.get_all_books()
        if not books:
            logger.warning("Nenhum livro encontrado no CSV. Abortando indexação.")
            return

        logger.info(f"Encontrados {len(books)} livros para indexar.")

        # 3. Preparar vetores para o upsert em lote
        vectors_to_upsert = []
        for book in tqdm(books, desc="Gerando Embeddings"):
            # Combina título e categoria para criar o embedding
            combined_text = f"Título: {book.title} Categoria: {book.category}"
            
            embedding = embedding_service.create_embedding(combined_text)
            
            # Prepara o metadado para busca futura
            metadata = {
                "title": book.title,
                "category": book.category,
                "rating": book.rating,
                "price": book.price,
                "image_url": book.image_url
            }
            
            vectors_to_upsert.append({
                "id": str(book.id),
                "values": embedding,
                "metadata": metadata
            })

        # 4. Enviar os vetores para o Pinecone em lotes (se necessário)
        batch_size = 100
        for i in tqdm(range(0, len(vectors_to_upsert), batch_size), desc="Enviando para o Pinecone"):
            batch = vectors_to_upsert[i:i + batch_size]
            pinecone_repo.upsert_vectors(batch)

        logger.info("Processo de indexação concluído com sucesso!")

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a indexação: {e}", exc_info=True)

if __name__ == "__main__":
    run_indexing()