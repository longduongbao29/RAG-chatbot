from elasticsearch import Elasticsearch
from injector import Injector, Module, singleton


from src.utils.tools.DateTime import DateTimeTool
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import DuckDuckGoSearchTool,DuckDuckGoSearch
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
from src.rag.strategy.retrieval.ElasticSearch.ElasticVectorSearch import ElasticVectorSearch, ElasticSearchTool
from src.rag.pipeline.LangGraph.ToolsType import Tools



class Dependency(Module):
    connection_provider = ConnectionProvider()
    config = Config()
    embedding_model = HFEmbeddingModel(config)
    elasticsearch = connection_provider.provide_connection(config)
    llm = LangchainGroqLLM(config)
    elastic_manager = ElasticManager(elasticsearch, embedding_model)
    elastic_vector_search = ElasticVectorSearch(elastic_manager)
    rag_fusion = RAGFusion(llm)
    elastic_vector_search = ElasticVectorSearch(elastic_manager)
    duckduckgo_search = DuckDuckGoSearchTool(DuckDuckGoSearch())
    datetime_tool = DateTimeTool()
    elastic_search_tool = ElasticSearchTool(elastic_vector_search,llm)
    def configure(self, binder):
        binder.bind(Config, to=self.config, scope=singleton)
        binder.bind(Elasticsearch, to=self.elasticsearch, scope=singleton)
        binder.bind(EmbeddingModel, to=self.embedding_model, scope=singleton)
        binder.bind(DbManager, to=self.elastic_manager, scope=singleton)
        binder.bind(LLM, to=self.llm, scope=singleton)
        binder.bind(QueryTranslation, to=self.rag_fusion)
        binder.bind(RetrievalStrategy, to=self.elastic_vector_search)
        binder.bind(LLMGenerator, to=LLMGenerator(self.llm))
        binder.bind(Tools, to= Tools([self.elastic_search_tool, self.duckduckgo_search, self.datetime_tool]))
    


injector = Injector([Dependency])