from regex import R
from src.rag.strategy.query_translation.QueryTranslation import QueryTranslation
from src.rag.strategy.query_translation.Prompts import RAG_FUSION_PROMPT
from src.rag.strategy.query_translation.Schemas import Query
class RAGFusion(QueryTranslation):
    """
    RAG Fusion strategy for query translation.
    """
    
    def translate(self, query: str):
        """
        Translate the query using RAG Fusion strategy.
        """
        # Implement the translation logic here
        chain = RAG_FUSION_PROMPT|self.llm
        translated_query:Query = chain.invoke({"query": query})
        return translated_query.queries