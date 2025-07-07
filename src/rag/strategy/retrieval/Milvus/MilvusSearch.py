from pydantic import Field
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
    def retrieve(self, collection_name:str, query:str, search_type: SearchStrategy = SearchStrategy.HYBRID, num_results:int=5)-> list[Document]:
        """
        Retrieve documents based on the query.
        """
   
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
            search_results = self.db_manager.hybrid_search(collection_name,query)
            docs_results = []
            for doc in search_results:
                docs_results.append(Document(id=doc["id"], content=doc["content"],  metadata=doc.get("metadata", {}),score=doc["distance"]))
        
       
        return docs_results
        
class MilvusSearchTool(BaseTool):
    
    name:str = "Milvus_search"
    description:str = "Search information from Milvus vector database"
    milvus_search: MilvusSearch = Field(default=None)
    reranker: Reranker = Field(default=None)
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