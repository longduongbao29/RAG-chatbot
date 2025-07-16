from src.embedding.MilvusEmbeddingModel import MilvusEmbeddingModel

embedding = MilvusEmbeddingModel()

print(embedding.embed("hello"))