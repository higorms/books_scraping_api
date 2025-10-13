import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from src.domain.exceptions import BookRepositoryException


load_dotenv()


class PineconeRepository:
    """Repositório para operações com banco vetorial Pinecone.

    Esta classe gerencia a conexão e operações básicas com o Pinecone,
    preparando a infraestrutura para embeddings e busca semântica.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: int = 1024
    ):
        """Inicializa a conexão com Pinecone.

        Args:
            api_key: API key do Pinecone
            index_name: Nome do índice
            dimension: Dimensão dos vetores
        """
        self.logger = logging.getLogger(__name__)

        try:
            self.api_key = os.getenv("PINECONE_API_KEY")
            self.index_name = os.getenv("PINECONE_INDEX_NAME")
            self.dimension = dimension

            if not self.api_key:
                raise BookRepositoryException(
                    "API key do Pinecone não foi encontrada",
                    "MISSING_API_KEY"
                )

            # Inicializa o cliente do Pinecone
            self.pc = Pinecone(api_key=self.api_key)

            # Congiguração do índice
            self._setup_index()

            self.logger.info(
                "Conexão com Pinecone estabelecida. "
                f"Índice: {self.index_name}"
            )

        except Exception as e:
            self.logger.error(
                f"Erro ao conectar com o Pinecone: {e}"
            )
            raise BookRepositoryException(
                f"Falha na conexão com o Pinecone: {e}",
                "CONNECTION_ERROR"
            )

    def _setup_index(self):
        """Configura o índice no Pinecone se não existir."""
        try:
            # Verificar se índice existe
            existing_indexes = [index.name for index in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                self.logger.info(
                    f"Criando novo índice: {self.index_name}"
                )

                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="euclidean",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                self.logger.info(
                    f"Índice {self.index_name} criado com sucesso."
                )

            # Conecta ao índice
            self.index = self.pc.Index(self.index_name)

        except Exception as e:
            raise BookRepositoryException(
                f"Erro ao configurar o índice Pinecone: {e}",
                "INDEX_SETUP_ERROR"
            )

    def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """Insere ou atualiza vetores no índice.

        Args:
            vectors: Lista de dicionários com 'id',
            'values' e opcionalmente 'metadata'

        Returns:
            bool: True se a operação foi bem-sucedida

        Raises:
            BookRepositoryException: Se houver erro na operação
        """
        try:
            self.index.upsert(vectors=vectors)
            self.logger.info(
                f"Inseridos {len(vectors)} vetores no Pinecone."
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao inserir os vetores; {e}"
            )
            raise BookRepositoryException(
                f"Falha ao inserir vetores no Pinecone: {e}",
                "UPSERT_ERROR"
            )

    def delete_vectors(self,
                       ids: List[str]
                       ) -> bool:
        """Remove vetores do índice.

        Args:
            ids: Lista de IDs dos vetores para remover

        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            self.index.delete(ids=ids)
            self.logger.info(
                f"Deletados {len(ids)} vetores do Pinecone."
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao deletar os vetores: {e}"
            )
            raise BookRepositoryException(
                f"Falha ao deletar vetores no Pinecone: {e}",
                "DELETE_ERROR"
            )

    def query_vectors(self,
                      vector: List[str],
                      top_k: int = 5,
                      include_metadata: bool = True
                      ) -> Dict[str, Any]:
        """Busca vetores similares.

        Args:
            vector: Vetor de consulta
            top_k: Número de resultados mais similares
            include_metadata: Se deve incluir metadados na resposta

        Returns:
            Dict com resultados da busca
        """
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=include_metadata
            )

            self.logger.info(
                "Consulta vetorial executada. "
                f"Top {top_k} resultados retornados."
            )
            return results

        except Exception as e:
            self.logger.error(
                f"Erro na consulta vetorial: {e}"
            )
            raise BookRepositoryException(
                f"Falha na consulta vetorial no Pinecone: {e}",
                "QUERY_ERROR"
            )

    def get_index_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice.

        Returns:
            Dict com estatísticas do índice
        """
        try:
            stats = self.index.describe_index_stats()
            return stats

        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            raise BookRepositoryException(
                f"Erro ao obter estatísticas do índice: {e}",
                "STATS_ERROR"
            )

    def health_check(self) -> bool:
        """Verifica se a conexão com Pinecone está funcionando.

        Returns:
            bool: True se a conexão está OK
        """
        try:
            # Tenta obter estatísticas como teste de conectividade
            self.get_index_stats()
            return True

        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            return False
