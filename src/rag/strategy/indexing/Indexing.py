

from src.rag.strategy.indexing.loader.LoaderRouter import LoaderRouter
from src.rag.strategy.indexing.chunking.Chunker import Chunker
from src.database.DbManager import DbManager
from src.utils.logger import setup_logger
from src.utils.helpers import session2collection
logger = setup_logger(__name__)

class Indexing:
    """
    Base class for indexing strategies.
    """
    def __init__(self, db_manager: DbManager, session_id:str,chunker: Chunker = None):
        self.collection_name = session2collection(session= session_id)
        self.db_manager = db_manager
        self.chunker = chunker
    def index_documents(self, file_path: str) -> None:
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
        self.db_manager.index(documents, self.collection_name)
        logger.info(f"Indexed {len(documents)} documents...")