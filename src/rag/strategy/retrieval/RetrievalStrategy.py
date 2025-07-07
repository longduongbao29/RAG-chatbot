from abc import ABC, abstractmethod

from src.utils.Document import Document

class RetrievalStrategy(ABC):
    """
    Abstract base class for retrieval strategies.
    """
    def __init__(self):
        """
        Initialize the retrieval strategy.
        """
    @abstractmethod
    def retrieve(self):
        """
        Retrieve documents based on the query.
        """
        pass
        


    