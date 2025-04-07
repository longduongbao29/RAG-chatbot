from enum import Enum

from src.llm.Schemas import LLMParams
from src.database.DbManager import DbManager
from src.config.config import config
from src.rag.pipeline.LangGraph.Graph import Graph
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.database.ElasticManager import ElasticManager, ConnectionProvider
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Status(Enum):
    FREE = 0
    BUSY = 1
class ChatService:
    def __init__(self, model_name:str, temperature:float, db_manager:DbManager) -> None:
        llm_params = LLMParams(model_name=model_name,temperature=temperature)
        self.service = Graph(llm_params,db_manager)
        self.status = Status.FREE
        self.db_manager = db_manager
        self.model_name = model_name
        self.temperature = temperature
class ChatServiceProvider:
    def __init__(self) -> None:
        super().__init__()
        self.services:list[ChatService] = []
    def dispatch(self, model_name, temperature, db_manager):
        for service in self.services:
            if service.status == Status.FREE and service.model_name == model_name and service.temperature == temperature:
                logger.info("Use available chat service")
                service.status = Status.BUSY
                return service
        new_service = ChatService(model_name=model_name, temperature=temperature, db_manager= db_manager)
        new_service.status = Status.BUSY
        self.services.append(new_service)
        logger.info("New chat service created")
        logger.info(f"Total number of chat services: {len(self.services)}")
        return new_service
    def recall(self, service:ChatService):
        service.status = Status.FREE
    def num_services(self):
        return len(self.services)

class ElasticConnectionSingleton:
    _instance = ConnectionProvider().provide_connection()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ElasticConnectionSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

class ElasticManagerProvider:
    def __init__(self) -> None:
        super().__init__()
        self.connection = ElasticConnectionSingleton()
    def create(self):
        service = ElasticManager(elasticsearch=self.connection, embedding=HFEmbeddingModel())
        return service
 