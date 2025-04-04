from math import log
from pydoc import doc
from injector import inject
from src.rag.pipeline.Handler import Handler
from src.rag.strategy.retrieval.RetrievalStrategy import RetrievalStrategy
from src.utils.logger import setup_logger
logger = setup_logger(__name__)
class RetrievalHandler(Handler):
    """
    Handler for document retrieval.
    """
    @inject
    def __init__(self, retrieval_strategy:RetrievalStrategy,index_name: str=None, next_handler: Handler = None):
        super().__init__(next_handler)
        self.retrieval_strategy = retrieval_strategy
        self.index_name = index_name
    def set_index_name(self, index_name: str):
        """
        Set the index name for the retrieval strategy.
        """
        self.index_name = index_name
    def handle(self,query:str, translated_query: list):
        """
        Handle the document retrieval.
        """
        if (self.index_name is None):
            return "No index name provided"
        logger.info(f"Retrieving documents for query: {query}")
        documents = []
        for q in translated_query:
            if isinstance(q, str):
                documents.append(self.retrieval_strategy.retrieve(self.index_name,q))
        # Pass the retrieved documents to the next handler
        return super().handle(query=query,retrieved_documents=self.retrieval_strategy.rerank(documents))