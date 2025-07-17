from langchain_groq import ChatGroq
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import DuckDuckGoSearch
from src.llm.Schemas import LLMParams
from src.rag.strategy.indexing.Indexing import Indexing
from src.database.MilvusManager import MilvusManager
from src.pipeline import CRAG, SelfRAG, NoRagPipeline
from src.llm.Provider import LLMProvider
from src.embedding.OpenAIEmbeddingModel import OpenAIEmbeddingModel
from src.api.models import RagStrategy
from src.rag.strategy.retrieval.Milvus.MilvusSearch import MilvusSearch
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Provider:
    db_manager = MilvusManager(OpenAIEmbeddingModel())
    def get_chat(self,session_id:str, provider:str, model_name: str, temperature: float, rag_strategy:RagStrategy, instruction:str = ""):
        llm_params = LLMParams(model_name=model_name, temperature=temperature, provider=provider)
        llm_provider = LLMProvider(llm_params)
        llm: ChatGroq | None = llm_provider.provide_llm()
        retriever = MilvusSearch(db_manager=self.db_manager, session_id = session_id)
        web_search = DuckDuckGoSearch()
        if rag_strategy == RagStrategy.C_RAG:
            self.chat_service = CRAG(llm =  llm, db_retriever = retriever, web_search_retriever=web_search)
        elif rag_strategy == RagStrategy.SELF_RAG:
            self.chat_service = SelfRAG(llm = llm, retriever = retriever)
        else:
            self.chat_service = NoRagPipeline(llm = llm,
                                              instruction = instruction)
        return self.chat_service
    def get_db_manager(self):
        return self.db_manager
    def get_indexer(self, session_id):
        return Indexing(db_manager=self.db_manager, session_id = session_id)