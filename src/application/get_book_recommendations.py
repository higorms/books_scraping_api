# src/application/get_book_recommendations.py

import logging
from typing import List
from src.domain.book import Book
from src.infrastructure.repositories.pinecone_repository import PineconeRepository
from src.infrastructure.repositories.book_csv_repository import BookRepository as BookCSVRepository
from src.infrastructure.services.embedding_service import EmbeddingService # <-- IMPORTANTE
from src.domain.exceptions import BookNotFoundError

# Renomeado para refletir a função real
class FindSimilarBooksByText:
    """
    Caso de uso para encontrar livros similares a um texto de busca.
    """
    def __init__(self, 
                 pinecone_repo: PineconeRepository, 
                 csv_repo: BookCSVRepository,
                 embedding_service: EmbeddingService):
        self.pinecone_repo = pinecone_repo
        self.csv_repo = csv_repo
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)

    def execute(self, query_text: str, top_k: int = 5) -> List[Book]:
        """
        Executa a busca semântica por livros.

        Args:
            query_text (str): O texto fornecido pelo usuário para a busca.
            top_k (int): Número de livros similares a retornar.

        Returns:
            List[Book]: Uma lista de 5 livros recomendados.
        """
        self.logger.info(f"Buscando livros similares para a consulta: '{query_text}'")

        try:
            # 1. Criar o embedding a partir do texto de busca do usuário
            query_vector = self.embedding_service.create_embedding(query_text)

            # 2. Consultar o Pinecone por vetores similares
            query_response = self.pinecone_repo.query_vectors(
                vector=query_vector,
                top_k=top_k,
                include_metadata=False 
            )

            # 3. Extrair os IDs dos livros recomendados
            recommended_ids = [int(match['id']) for match in query_response['matches']]
            
            if not recommended_ids:
                self.logger.warning(f"Nenhuma recomendação encontrada para a consulta: '{query_text}'")
                return []

            # 4. Buscar os detalhes completos dos livros recomendados no repositório CSV
            all_books = self.csv_repo.get_all_books()
            books_map = {book.id: book for book in all_books}

            # Garante que a ordem da similaridade seja mantida
            recommendations = [books_map[rec_id] for rec_id in recommended_ids if rec_id in books_map]
            
            self.logger.info(f"Retornando {len(recommendations)} recomendações.")
            return recommendations

        except Exception as e:
            self.logger.error(f"Erro ao obter recomendações: {e}", exc_info=True)
            raise