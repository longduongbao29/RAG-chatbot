
from elasticsearch import Elasticsearch
from injector import Injector, Module, singleton

from src.config.config import Config
from src.llm.LLM import LLM
from src.llm.langchain_groq_llm import LangchainGroqLLM
from src.database.DbManager import DbManager
from src.database.ElasticManager import ConnectionProvider, ElasticManager
from src.embedding.EmbeddingModel import EmbeddingModel
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.rag.strategy.query_translation.QueryTranslation import QueryTranslation
from src.rag.strategy.query_translation.RagFusion import RAGFusion
from src.rag.strategy.generation.Generation import LLMGenerator
from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy
from src.rag.strategy.retrieval.ElasticSearch.ElasticVectorSearch import ElasticVectorSearch

class Dependency(Module):
    def configure(self, binder):
        connection_provider = ConnectionProvider()
        config = Config()
        embedding_model = HFEmbeddingModel(config)
        elasticsearch = connection_provider.provide_connection(config)
        elastic_manager = ElasticManager(elasticsearch, embedding_model)
        binder.bind(Config, to=config, scope=singleton)
        binder.bind(Elasticsearch, to=elasticsearch, scope=singleton)
        binder.bind(EmbeddingModel, to=embedding_model, scope=singleton)
        binder.bind(DbManager, to=elastic_manager, scope=singleton)
        
        llm = LangchainGroqLLM(config)
        binder.bind(LLM, to=llm)
        
        rag_fusion = RAGFusion(llm)
        binder.bind(QueryTranslation, to=rag_fusion)
        
        retrieval_strategy = ElasticVectorSearch(elastic_manager)
        binder.bind(RetrievalStrategy, to=retrieval_strategy)
        
        binder.bind(LLMGenerator, to=LLMGenerator(llm))

injector = Injector([Dependency])