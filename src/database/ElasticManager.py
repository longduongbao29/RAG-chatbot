from injector import inject
from elasticsearch import Elasticsearch

from src.embedding.EmbeddingModel import EmbeddingModel
from src.embedding.HFEmbeddingModel import HFEmbeddingModel
from src.config.config import Config
from src.database.DbManager import DbManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionProvider:
    def provide_connection(self, configuration: Config) -> Elasticsearch:
        logger.info("Connecting to Elasticsearch...")
        elasticsearch = Elasticsearch(configuration.ELASTIC_ENDPOINT, 
                                      api_key=configuration.ELASTIC_API_KEY, 
                                      ca_certs=configuration.ELASTIC_CERT_PATH, 
                                      timeout=30, 
                                      retry_on_timeout=True)
        if not elasticsearch.ping():
            logger.error("Elasticsearch connection failed.")
            raise Exception("Elasticsearch connection failed.")
        logger.info("Elasticsearch connection successful.")
        return elasticsearch
class ElasticManager(DbManager):
    @inject
    def __init__(self, elasticsearch: Elasticsearch, embedding : EmbeddingModel):
        self.elasticsearch = elasticsearch
        self.embedding = embedding
    def init_index(self, index_name: str):
        """
        Initialize an index in Elasticsearch.
        """
        logger.info("Initializing index %s in Elasticsearch...", index_name)
        if not self.elasticsearch.indices.exists(index=index_name):
            self.elasticsearch.indices.create(
                    index=index_name,
                    settings={
                            "index": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                            }
                        },
                    mappings={
                        "properties": {
                            "id": {
                                "type": "text"
                            },
                            "content": {
                                "type": "text"

                            },
                            "dense_vector": {
                                "type": "dense_vector",
                                "dims": 768
                            },           
                        }
                    },
                )
            logger.info("Index %s created.", index_name)
        else:
            logger.info("Index %s already exists.", index_name)
            
    def check_health(self):
        logger.info("Checking Elasticsearch health...")
        health = self.elasticsearch.cluster.health()
        logger.info("Status: %s", health['status'])
        
    def index(self, index_name: str, document: dict):
        """
        Index a document in Elasticsearch.
        """
        logger.info("Indexing document in Elasticsearch...")
        document['dense_vector'] = self.embedding.embed(text=document['content'])
        response = self.elasticsearch.index(index=index_name, document=document)
        logger.info("Document indexed with ID: %s", response['_id'])
        return response
    
    def search(self, index_name: str, query: dict):
        """
        Search for documents in Elasticsearch.
        """
        logger.info("Searching for documents in Elasticsearch...")
        response = self.elasticsearch.search(index=index_name, body=query)
        logger.info("Search results: %s", response['hits']['hits'])
        return response['hits']['hits']
    
    def fulltext_search(self, index_name: str, query: str, num_results: int = 5)-> list[dict]:
        """
        Perform a full-text search in Elasticsearch.
        """
        body = {
            "query": {
                "match": {
                    "content": query
                }
            }
        }
        response = self.elasticsearch.search(index=index_name, body=body)
        return response['hits']['hits'][:num_results]
    
    def semantic_search(self, index_name: str, query: str, num_results: int = 5)-> list[dict]:
        """
        Perform a semantic search in Elasticsearch.
        """
        query_vector = self.embedding.embed(query)
        if len(query_vector) != 768:
            logger.error("Query vector dimensions do not match the expected dimensions (768).")
            raise ValueError("Query vector dimensions mismatch.")

        body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'dense_vector') + 1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            }
        }
        response = self.elasticsearch.search(index=index_name, body=body)
        
        # Log the results for debugging
        # logger.info("Semantic search results: %s", response['hits']['hits'])
        
        # Return sorted results
        return response['hits']['hits'][:num_results]