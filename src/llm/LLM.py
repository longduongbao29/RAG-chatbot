from abc import ABC, abstractmethod


class LLM(ABC):
    """
    Abstract base class for Language Models (LLMs).
    """
    model_name:str
    temperature:float
    @abstractmethod
    def generate() -> str:
        """
        Generate text based on the provided prompt.
        """
        pass

