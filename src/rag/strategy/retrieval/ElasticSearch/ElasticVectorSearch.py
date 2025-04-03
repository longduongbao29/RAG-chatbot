from src.rag.strategy.retrieval.Types import SearchStrategy
from src.rag.strategy.retrieval.VectorSearch import VectorSearch

class ElasticVectorSearch(VectorSearch):
    """
    Elastic vector search strategy for document retrieval.
    """
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        
    def retrieve(self, query:str, search_type: SearchStrategy):
        """
        Retrieve documents based on the query.
        """
        # Implement the retrieval logic using Elasticsearch
        if search_type == SearchStrategy.FULL_TEXT:
            return self.db_manager.fulltext_search(query)
        elif search_type == SearchStrategy.SEMANTIC:
            return self.db_manager.semantic_search(query)
        elif search_type == SearchStrategy.HYBRID:
            # Implement hybrid search logic
            return self.rerank()
    