

from src.rag.strategy.indexing.loader.LoaderRouter import LoaderRouter
from src.rag.strategy.indexing.chunking.Chunker import Chunker
from src.utils.Document import Document
from src.database.DbManager import DbManager
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

class Indexing:
    """
    Base class for indexing strategies.
    """
    def __init__(self, db_manager: DbManager, chunker: Chunker = None):
        self.db_manager = db_manager
        self.chunker = chunker
    def index_documents(self, file_path: str, collection_name:str) -> None:
        """
        Index a list of documents.
        """
        loader = LoaderRouter(file_path).router()
        
        if not self.chunker:
            logger.info("Using default chunker...")
            documents = Chunker.default_chunk_text(loader.text)
            logger.info(f"Chunking text using default chunker...{len(documents)} chunks created.")
        else:
            documents = self.chunker.chunk_text(loader.text)
        self.db_manager.create_collection(collection_name)
        self.db_manager.index(documents, collection_name)
        logger.info(f"Indexed {len(documents)} documents...")