from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_core.tools.base import BaseTool

from src.rag.strategy.retrieval.Reranker import Reranker
from src.utils.Document import Document
from src.database.DbManager import DbManager
from src.rag.strategy.retrieval.Types import SearchStrategy
from src.rag.strategy.retrieval.VectorSearch import VectorSearch
from src.utils.logger import setup_logger
logger = setup_logger(__name__)
class MilvusSearch(VectorSearch):
    def __init__(self, db_manager:DbManager):
        """
        Milvus vector search strategy for document retrieval.
        """
        super().__init__()
        self.db_manager = db_manager
    
    def get_documents(self, doc_dict:list[dict])-> list[Document]:
        """
        Convert a list of dictionaries to a list of Document objects.
        """
        docs = []
        for doc in doc_dict:
            docs.append(Document(id=doc["id"], content=doc["content"], metadata=doc.get("metadata", {}), score=doc["distance"]))
        return docs
    def retrieve(self, **kwargs)-> list[Document]:
        """
        Retrieve documents based on the query.
        """
        logger.info("Retrieving documents from Milvus...")
        query: str = kwargs.get("query", "")
        collection_name = kwargs.get("collection_name", "default_collection")
        search_type = kwargs.get("search_type")
        if search_type:
            search_type = SearchStrategy(search_type)
        else:
            search_type = SearchStrategy.HYBRID
        num_results = kwargs.get("num_results", 5)

        logger.info(f"Query: {query}, Collection: {collection_name}, Search Type: {search_type}, Num Results: {num_results}")
        docs_results = []

        if search_type == SearchStrategy.FULL_TEXT:
            search_results = self.db_manager.fulltext_search(collection_name,query)
            docs_results = []
            for doc in search_results:
                docs_results.append(Document(id=doc["id"], content=doc["content"],  metadata=doc.get("metadata", {}),score=doc["distance"]))
          
        elif search_type == SearchStrategy.SEMANTIC:
            search_results = self.db_manager.semantic_search(collection_name,query)
            docs_results = []
            for doc in search_results:
                docs_results.append(Document(id=doc["id"], content=doc["content"],  metadata=doc.get("metadata", {}),score=doc["distance"]))
         
        elif search_type == SearchStrategy.HYBRID:
            logger.info("Performing hybrid search...")
            search_results = self.db_manager.hybrid_search(collection_name = collection_name,query = query)
            docs_results = []
            for doc in search_results:
                docs_results.append(Document(id=doc["id"], content=doc["content"],  metadata=doc.get("metadata", {}),score=doc["distance"]))
        
       
        return docs_results

class MilvusArgsSchema(BaseModel):
    """Arguments schema for Milvus search tool."""
    query: str = Field(..., description="The query string to search for.")
    translated_queries: list = Field(default_factory=list, description="Multiquery for better retrieval.")
    collection_name: str = Field(default="default_collection", description="The name of the collection to search in.")
    search_type: SearchStrategy = Field(default=SearchStrategy.HYBRID, description="The type of search to perform.")
    num_results: int = Field(default=5, description="Number of results to return.")
class MilvusSearchTool(BaseTool):
    
    name:str = "Milvus_search"
    description: str = "Search documents in Milvus using vector search."
    args_schema: Type[BaseModel] = MilvusArgsSchema # type: ignore
    milvus_search: Optional[MilvusSearch] = Field(default=None)
    reranker: Optional[Reranker] = Field(default=None)
    def __init__(self, milvus_search: MilvusSearch, reranker: Reranker, **kwargs):
        super().__init__( **kwargs)
        self.milvus_search = milvus_search
        self.reranker = reranker
    def _run(self, **args):
        query: str = args["query"]
        translated_queries:list = args["translated_queries"]
        collection_name: str = args.get("collection_name", "default_collection")
        search_type = args.get("search_type", SearchStrategy.HYBRID)
        num_results = args.get("num_results", 5)
        queries:list = [query] + translated_queries
        docs_retrieved = []
        for q in queries:
            docs_retrieved.append(self.milvus_search.retrieve(collection_name=collection_name,
                            query=q,
                            search_type=search_type,
                            num_results=num_results))
        rerank_docs = self.reranker.rerank(docs_retrieved, topk=num_results)
        context = "\n".join([doc.content for doc in rerank_docs])
        return context