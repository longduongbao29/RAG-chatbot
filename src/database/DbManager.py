from abc import ABC, abstractmethod
from typing import Any

class DbManager(ABC):
    @abstractmethod
    def index(self):
        pass
    # @abstractmethod
    # def delete(self):
    #     pass
    @abstractmethod
    def create_collection(self, collection_name: str) -> None:
        """Create a new collection in the database."""
        pass
    @abstractmethod
    def create_database(self, db_name: str) -> None:
        """Create a new database."""
        pass
    @abstractmethod
    def hybrid_search(self):
        """Perform a hybrid search combining full-text and semantic search.
        """
        pass
    @abstractmethod
    def fulltext_search(self, index:str, query:str, num_results:int=5)-> list[dict]:
        """
        Perform a full-text search.
        """
        pass
    @abstractmethod
    def semantic_search(self, index:str, query:str, num_results:int=5)-> list[dict]:
        """
        Perform a semantic search.
        """
        pass

