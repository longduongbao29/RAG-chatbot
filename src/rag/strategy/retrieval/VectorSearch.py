from abc import ABC

from src.database.DbManager import DbManager
from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy

class VectorSearch(RetrievalStrategy, ABC):
    """
    Vector search strategy for document retrieval.
    """
    
    def __init__(self, db_manager: DbManager):
        self.db_manager = db_manager
    
    