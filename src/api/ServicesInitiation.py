from src.rag.strategy.indexing.Indexing import Indexing
from src.database.MilvusManager import MilvusManager
from src.rag.pipeline.ChatPipeline import ChatPipeline
from src.rag.pipeline.NoRagPipeline import NoRagPipeline
from src.llm.Schemas import LLMParams
from src.rag.pipeline.LangGraph.Graph import Graph
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Provider:
    db_manager = MilvusManager(HFEmbeddingModel())
    indexer = Indexing(db_manager=db_manager)
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
    def get_indexer(self):
        return self.indexer