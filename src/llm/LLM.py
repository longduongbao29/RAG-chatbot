from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel

class LLM(ABC):
    """
    Abstract base class for Language Models (LLMs).
    """
    model_name:str
    temperature:float
    @abstractmethod
    def generate(self) -> str:
        """
        Generate text based on the provided prompt.
        """
        pass
    @abstractmethod
    def get_llm(self)->BaseChatModel:
        """
        Get the LLM instance.
        """
        pass
