from importlib import metadata
from injector import inject
from elasticsearch import Elasticsearch

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
    def __init__(self, elasticsearch: Elasticsearch):
        self.elasticsearch = elasticsearch

    def init_index(self, index_name: str):
        """
        Initialize an index in Elasticsearch.
        """
        logger.info("Initializing index %s in Elasticsearch...", index_name)
        if not self.elasticsearch.indices.exists(index=index_name):
            self.elasticsearch.indices.create(
                    index=index_name,
                    mappings={
                        "properties": {
                            "id": {
                                "type": "text"
                            },
                            "content": {
                                "type": "semantic_text",
                                "inference_id": "embedding_inf"
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
        response = self.elasticsearch.index(index=index_name, body=document)
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
    
    def fulltext_search(self, index_name: str, query: str):
        """
        Perform a full-text search in Elasticsearch.
        """
        logger.info("Performing full-text search in Elasticsearch...")
        body = {
            "query": {
                "match": {
                    "content": query
                }
            }
        }
        response = self.elasticsearch.search(index=index_name, body=body)
        logger.info("Full-text search results: %s", response['hits']['hits'])
        return response['hits']['hits']
    
    def semantic_search(self, index_name: str, query_vector: list):
        """
        Perform a semantic search in Elasticsearch.
        """
        logger.info("Performing semantic search in Elasticsearch...")
        body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            }
        }
        response = self.elasticsearch.search(index=index_name, body=body)
        logger.info("Semantic search results: %s", response['hits']['hits'])
        return response['hits']['hits']