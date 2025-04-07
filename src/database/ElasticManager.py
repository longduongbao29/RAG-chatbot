from uuid import uuid4
from injector import inject
from elasticsearch import Elasticsearch, helpers

from src.embedding.EmbeddingModel import EmbeddingModel
from src.config.config import config
from src.database.DbManager import DbManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionProvider:
    def provide_connection(self) -> Elasticsearch:
        logger.info("Connecting to Elasticsearch...")
        elasticsearch = Elasticsearch(config.ELASTIC_ENDPOINT, 
                                      api_key=config.ELASTIC_API_KEY, 
                                      ca_certs=config.ELASTIC_CERT_PATH, 
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
        self.client = elasticsearch
        self.embedding = embedding     
        self.init_index_descriptions()
    def init_index_descriptions(self):
        if not self.client.indices.exists(index="index_descriptions"):
            self.client.indices.create(
                    index="index_descriptions",
                    settings={
                            "index": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                            }
                        },
                    mappings={
                        "properties": {
                            "index": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            },        
                        }
                    },
                )
    def init_index(self, index_name: str, description: str):
        """
        Initialize an index in Elasticsearch.
        """
        logger.info("Initializing index %s in Elasticsearch...", index_name)
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(
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
            self.client.index(index="index_descriptions",document=
                                     {
                                       "index":index_name,
                                       "description": description  
                                     })
            logger.info("Index %s created.", index_name)
        else:
            logger.info("Index %s already exists.", index_name)
            
    def check_health(self):
        logger.info("Checking Elasticsearch health...")
        health = self.client.cluster.health()
        logger.info("Status: %s", health['status'])
        
    def index(self, index_name: str, text: str):
        """
        Index a document in Elasticsearch.
        """
        document =  {
            "id": str(uuid4()),
            "content": text,
            'dense_vector' : self.embedding.embed(text=text)
        }
        logger.info(f"Indexing 1 document into {index_name}...")
        response = self.client.index(index=index_name, document=document)
        logger.info("Document indexed with ID: %s", response['_id'])
        return response
    def bulk_index(self,index_name,chunks:list):
        logger.info(f"Indexing {len(chunks)} documents into {index_name}...")
        actions = []
        for chunk in chunks:
            actions.append( {
                            "_op_type": "index", 
                            "_index": index_name,  
                            "_source": {
                                "id": str(uuid4()),
                                "content": chunk,
                                "dense_vector":self.embedding.embed(text=chunk)
                            }
                        })
        try:
            helpers.bulk(self.client, actions)
            logger.info("Index successfully!")
        except Exception as e:
            logger.info(f"Indexing Failed due to error: {e}")
    def search(self, index_name: str, query: dict):
        """
        Search for documents in Elasticsearch.
        """
        logger.info("Searching for documents in Elasticsearch...")
        response = self.client.search(index=index_name, body=query)
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
        try:
            response = self.client.search(index=index_name, body=body)
        except Exception as e:
            logger.error("Full-text search failed: %s", e)
            return []
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
        try:
            response = self.client.search(index=index_name, body=body)
        except Exception as e:
            logger.error("Semantic search failed: %s", e)
            return []
        return response['hits']['hits'][:num_results]