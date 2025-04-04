from math import log
from injector import inject
from src.rag.strategy.query_translation.QueryTranslation import QueryTranslation
from src.rag.pipeline.Handler import Handler
from src.utils.logger import setup_logger
logger = setup_logger(__name__)
class QueryTranslationHandler(Handler):
    """
    Handler for query translation.
    """
    @inject
    def __init__(self, query_translation:QueryTranslation, next_handler: Handler = None):
        super().__init__(next_handler)
        self.query_translation = query_translation
        
    
    def handle(self, query: str):
        """
        Handle the query translation.
        """
        logger.info(f"Handling query translation for: {query}")
        # Implement the query translation logic here
        translated_query = self.query_translation.translate(query)
        logger.info(f"Translated query: {translated_query}")
        # Pass the translated query to the next handler
        return super().handle(query=query, translated_query=translated_query)
    