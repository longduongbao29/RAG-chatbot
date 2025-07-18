from langchain_openai.embeddings.base import OpenAIEmbeddings

from src.embedding.EmbeddingModel import EmbeddingModel
from src.config.config import config
class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self):
        self.embedding = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY,
                                          model= config.OPENAI_EMBEDDING_MODEL,
                                          dimensions=config.EMBEDDING_DIM)
        
    def embed(self, text):
        return self.embedding.embed_query(text=text)