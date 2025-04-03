

from enum import Enum

class RetrievalType(Enum):
    """
    Enum class for different retrieval types.
    """
    BM25 = "BM25"
    ELASTIC_VECTOR = "ElasticVector"

class SearchStrategy(Enum):
    """
    Enum class for different retrieval strategy types.
    """
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

