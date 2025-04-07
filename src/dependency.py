from elasticsearch import Elasticsearch
from injector import Injector, Module, singleton

from src.config.config import Config
from src.llm.LLM import LLM
from src.database.DbManager import DbManager
from src.embedding.EmbeddingModel import EmbeddingModel
from src.rag.strategy.query_translation.QueryTranslation import QueryTranslation
from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy
from src.rag.pipeline.LangGraph.ToolsType import Tools
from src.database.ElasticManager import ConnectionProvider
from src.database.ElasticManager import  ElasticManager
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.llm.langchain_groq_llm import LangchainGroqLLM
from src.rag.strategy.query_translation.RagFusion import RAGFusion
from src.rag.strategy.retrieval.ElasticSearch.ElasticVectorSearch import ElasticVectorSearch, ElasticSearchTool
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import DuckDuckGoSearchTool,DuckDuckGoSearch
from src.utils.tools.DateTime import DateTimeTool
class Dependency(Module):
    #singleton
    config = Config()
    elasticsearch = ConnectionProvider().provide_connection()
    
    def configure(self, binder):
        binder.bind(Config, to=self.config, scope=singleton)
        binder.bind(Elasticsearch, to=self.elasticsearch, scope=singleton)
        
        binder.bind(DbManager,
                    to=ElasticManager(self.elasticsearch, 
                                    HFEmbeddingModel(self.config)))
        binder.bind(EmbeddingModel,
                    to=HFEmbeddingModel(self.config))
        binder.bind(LLM, to=LangchainGroqLLM(self.config))
        binder.bind(QueryTranslation,
                    to= RAGFusion(LangchainGroqLLM(self.config)))
        binder.bind(RetrievalStrategy,
                    to=ElasticVectorSearch(ElasticManager(self.elasticsearch, 
                                            HFEmbeddingModel(self.config))))
        binder.bind(Tools, to= Tools([ElasticSearchTool(LangchainGroqLLM(self.config)),
                                      DuckDuckGoSearchTool(DuckDuckGoSearch()),
                                      DateTimeTool()]))
    


injector = Injector([Dependency])