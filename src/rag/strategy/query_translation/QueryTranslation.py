from abc import ABC, abstractmethod
from injector import inject

from src.llm.LLM import LLM
from src.rag.strategy.query_translation.Schemas import Query
class QueryTranslation(ABC):
    """
    Abstract base class for query translation strategies.
    """
    @inject
    def __init__(self, llm: LLM):
        self.llm = llm.get_llm().with_structured_output(Query)
    
    @abstractmethod
    def translate(self, query: str, history:str)->list[str]:
        """
        Translate the query using the specific strategy.
        """
        pass