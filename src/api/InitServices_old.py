from math import e
from src.rag.pipeline.ChatPipeline import ChatPipeline
from src.rag.pipeline.NoRagPipeline import NoRagPipeline
from src.llm.Schemas import LLMParams
from src.rag.pipeline.LangGraph.Graph import Graph
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.database.ElasticManager import ElasticManager, ConnectionProvider
from src.utils.logger import setup_logger
from src.config.config import config

logger = setup_logger(__name__)

class ElasticConnectionSingleton:
    _instance = ConnectionProvider().provide_connection()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ElasticConnectionSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

class Provider:
    db_manager = ElasticManager(elasticsearch=ElasticConnectionSingleton(), embedding=HFEmbeddingModel())

    def get_chat(self, model_name: str, temperature: float, use_retrieve: bool,tools:list, instruction:str = None)-> ChatPipeline:
        if use_retrieve:
            self.chat_service = Graph(
                LLMParams(model_name=model_name, temperature=temperature),
                self.db_manager,
                tools,
                instruction,
            )
        else:
            self.chat_service = NoRagPipeline(LLMParams(model_name=model_name,temperature=temperature)
                                              ,instruction)
        return self.chat_service
    def get_db_manager(self):
        return self.db_manager
