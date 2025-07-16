from pymilvus import model

from src.config.config import config
from src.embedding.EmbeddingModel import EmbeddingModel

class MilvusEmbeddingModel(EmbeddingModel):
    def __init__(self):
        self.model_name = config.EMBEDDING_MODEL_NAME
        self.embeddings = model.DefaultEmbeddingFunction()
    def embed(self, text):
        return self.embeddings._to_embedding(text)