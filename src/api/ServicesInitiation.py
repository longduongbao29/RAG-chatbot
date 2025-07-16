from langchain_groq import ChatGroq
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import DuckDuckGoSearch
from src.llm.Schemas import LLMParams
from src.rag.strategy.indexing.Indexing import Indexing
from src.database.MilvusManager import MilvusManager
from src.pipeline.ChatPipeline import ChatPipeline
from src.pipeline.NoRagPipeline import NoRagPipeline
from src.llm.Provider import LLMProvider
from src.embedding.MilvusEmbeddingModel import MilvusEmbeddingModel
from src.pipeline.CRAG.Graph import CRAG
from src.rag.strategy.retrieval.Milvus.MilvusSearch import MilvusSearch
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Provider:
    db_manager = MilvusManager(MilvusEmbeddingModel())
    indexer = Indexing(db_manager=db_manager)
    def get_chat(self, model_name: str, temperature: float, use_retrieve: bool,tools:list, instruction:str = "")-> ChatPipeline:
        llm_params = LLMParams(model_name=model_name, temperature=temperature, provider="groq")
        llm_provider = LLMProvider(llm_params)
        llm: ChatGroq | None = llm_provider.provide_llm()
        retriever = MilvusSearch(db_manager=self.db_manager)
        web_search = DuckDuckGoSearch()
        if use_retrieve:
            self.chat_service = CRAG(llm =  llm, db_retriever = retriever, web_search_retriever=web_search)
        else:
            self.chat_service = NoRagPipeline(LLMParams(model_name=model_name,temperature=temperature)
                                              ,instruction)
        return self.chat_service
    def get_db_manager(self):
        return self.db_manager
    def get_indexer(self):
        return self.indexer