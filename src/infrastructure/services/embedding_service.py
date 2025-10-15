from sentence_transformers import SentenceTransformer
import logging

class EmbeddingService:
    """
    Serviço para gerar embeddings de texto usando um modelo pré-treinado.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Inicializa o serviço, carregando o modelo do sentence-transformers.

        Args:
            model_name (str): O nome do modelo a ser usado da biblioteca sentence-transformers.
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.model = SentenceTransformer(model_name)
            self.logger.info(f"Modelo de embedding '{model_name}' carregado com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao carregar o modelo de embedding: {e}")
            raise

    def create_embedding(self, text: str) -> list[float]:
        """
        Cria um embedding para um dado texto.

        Args:
            text (str): O texto a ser convertido em vetor.

        Returns:
            list[float]: O vetor de embedding gerado.
        """
        return self.model.encode(text).tolist()