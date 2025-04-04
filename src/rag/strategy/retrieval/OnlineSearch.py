from abc import ABC, abstractmethod
from langchain_core.tools.base import BaseTool
from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy

class OnlineSearch(RetrievalStrategy):
    """
    OnlineSearch is a class that implements the RetrievalStrategy interface.
    It is used for online search retrieval strategy.
    """
    tool: BaseTool= None
    @abstractmethod
    def search(self, query: str, **kwargs):
        """
        Perform an online search based on the query.
        """
        pass
    