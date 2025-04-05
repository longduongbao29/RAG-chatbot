from injector import inject
from src.rag.pipeline.SimplePipeline.Handler import Handler
from src.rag.strategy.generation.Generation import LLMGenerator
from src.utils.Document import Document
from src.utils.logger import setup_logger
logger = setup_logger(__name__)
class GenerationHandler(Handler):
    """
    Handler for document generation.
    """
    @inject
    def __init__(self,generator:LLMGenerator, next_handler: Handler = None):
        super().__init__(next_handler)
        self.generator = generator
    def handle(self,query:str, retrieved_documents: list[Document]):
        """
        Handle the document generation.
        """
        context = "\n".join([d.content for d in retrieved_documents])
        return self.generator.generate(query=query, context=context)