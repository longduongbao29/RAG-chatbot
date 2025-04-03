from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.
    """
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """
        Embed the provided text into a vector representation.
        """
        pass