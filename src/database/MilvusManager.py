from pymilvus import AnnSearchRequest, MilvusClient, CollectionSchema, FieldSchema, DataType, Function, FunctionType, RRFRanker
from pymilvus import MilvusException

from src.database.DbManager import DbManager
from src.config.config import config
from src.utils.logger import setup_logger
from src.embedding.EmbeddingModel import EmbeddingModel
from src.utils.Document import Document

logger = setup_logger(__name__)

class MilvusConfig:
    bm25_function = Function(
        name="bm25_fn",
        input_field_names=["content"],
        output_field_names="sparse_vector",
        function_type=FunctionType.BM25,
    )

    analyzer_params = {"tokenizer": "standard", "filter": ["lowercase"]}
    schema = CollectionSchema(
        fields=[
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content",
                        dtype=DataType.VARCHAR,  
                        max_length=65535,
                        analyzer_params=analyzer_params,
                        enable_match=True,  # Enable text matching
                        enable_analyzer=True),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIM),
            FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
            FieldSchema(name="metadata", dtype=DataType.JSON, is_nullable=True)
        ],
        description="RAG schema for Milvus",
    ) 
    schema.add_function(bm25_function)

    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="BM25",
    )
    index_params.add_index(field_name="dense_vector", index_type="FLAT", metric_type="IP")


class MilvusManager(DbManager):
    def __init__(self, embedding_model:EmbeddingModel):
        self.client  =  MilvusClient(
                                        uri=config.MILVUS_URI,
                                        token=config.MILVUS_TOKEN
                                    )
        self.embedding_model = embedding_model
        self.create_database(config.MILVUS_DB_NAME)

    def create_database(self, db_name: str):
        """
        Create a database in Milvus.
        """
        logger.info("Creating database %s in Milvus...", db_name)
        try:
            self.client.create_database(db_name)
            logger.info("Database %s created successfully.", db_name)
        except MilvusException as e:
            logger.warning("Database %s already exists.")
        self.client.use_database(
            db_name=db_name
        )
    def create_collection(self, collection_name: str):
        """
        Create a collection in Milvus.
        """
        if not self.client.has_collection(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                schema=MilvusConfig.schema,
                properties={"collection.ttl.seconds": 1209600},
                index_params=MilvusConfig.index_params
            )

            logger.info("Collection %s created successfully.", collection_name)
    def delete_collection(self, collection_name:str):
        if self.client.has_collection(collection_name):
            self.client.drop_collection(collection_name=collection_name)
    def index(self, documents: list[Document], collection_name: str):
        try:
            entities = []

            for doc in documents:
                embedding =  self.embedding_model.embed(text=doc.content)
                entities.append(
                    {
                        "content": doc.content,
                        "dense_vector": embedding,
                        "metadata": doc.metadata,
                    }
                )
            self.client.insert(collection_name, entities)
        except Exception as e:
            logger.error(f"At {__name__}: {e}")
            raise e
    def fulltext_search(self, collection_name:str, query:str, num_results = 10):
        results = self.client.search(
                collection_name=collection_name,
                data=[query],
                anns_field="sparse_vector",
                limit=num_results,
                output_fields=["content", "metadata"],
        )
        sparse_results = results[0]

        return sparse_results
        
    def semantic_search(self, collection_name:str , query:str, num_results = 10):
        query_embedding = self.embedding_model.embed(text=query)

        # Semantic search using dense vectors
        results = self.client.search(
            collection_name=collection_name,
            data=[query_embedding],
            anns_field="dense_vector",
            limit=num_results,
            output_fields=["content", "metadata"],
        )
        dense_results = results[0]

        return dense_results
    def hybrid_search(self, collection_name: str, query: str, num_results: int = 20):
        """
        Perform a hybrid search in Milvus.
        """
        query_embedding = self.embedding_model.embed(text=query)

        # Set up BM25 search request
        sparse_search_params = {"metric_type": "BM25"}
        sparse_request = AnnSearchRequest(
            [query], "sparse_vector", sparse_search_params, limit=num_results
        )

        # Set up dense vector search request
        dense_search_params = {"metric_type": "IP"}
        dense_request = AnnSearchRequest(
            [query_embedding], "dense_vector", dense_search_params, limit=num_results
        )

        # Perform hybrid search with reciprocal rank fusion
        results = self.client.hybrid_search(
            collection_name,
            [sparse_request, dense_request],
            ranker=RRFRanker(),  # Reciprocal Rank Fusion for combining results
            limit=5,
            output_fields=["content", "metadata"],
        )
        hybrid_results = []
        if results:
            hybrid_results = results[0]
        return hybrid_results
   