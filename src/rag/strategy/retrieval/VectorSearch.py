from abc import abstractmethod

from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy

class VectorSearch(RetrievalStrategy):
    """
    Vector search strategy for document retrieval.
    """
        
    @abstractmethod
    def retrieve(self, query: str):
        """
        Retrieve documents based on the query.
        """
        pass
    
    