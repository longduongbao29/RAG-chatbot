
from uuid import uuid4
from src.database.ElasticManager import ElasticManager
from test_rag.dependency import injector

from test_rag.datas import data1, data2, data3
manager = injector.get(ElasticManager)

def index(index_name: str, text:str):
    """
    Initialize an index in Elasticsearch.
    """
    manager.init_index(index_name)
    
    doc = {
        "id": str(uuid4()),
        "content": text,
    }
    manager.index(index_name, doc)
    

index("test_index", data1)
index("test_index", data2)
index("test_index", data3)