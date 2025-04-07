from venv import logger
from injector import inject
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


from src.config.config import config
from src.embedding.EmbeddingModel import EmbeddingModel
from src.utils.logger import setup_logger

logger  = setup_logger(__name__)

class HFEmbeddingModel(EmbeddingModel):
    
    @inject
    def __init__(self):
        """
        Initialize the Hugging Face embedding model.
        """
        self.model_name = config.EMBEDDING_MODEL_NAME
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
       
    def embed(self, text: str) -> list[float]:
        """
        Embed the provided text using the Hugging Face model.
        """
        try:
            embedding = self.embeddings.embed_query(text)
        except (Exception) as e:
            logger.error(f"Error in Hugging Face embedding: {e}")
        return embedding