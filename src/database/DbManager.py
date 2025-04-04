from abc import ABC, abstractmethod

class DbManager(ABC):
    @abstractmethod
    def check_health(self):
        """
        Check database health.
        """
        return None
    @abstractmethod
    def index(self):
        pass
    # @abstractmethod
    # def delete(self):
    #     pass
    @abstractmethod
    def search(self):
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

