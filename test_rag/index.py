
from src.database.ElasticManager import ElasticManager
from src.rag.strategy.chunking.loader.PDFLoader import PDFLoader
from src.rag.strategy.chunking.loader.DocxLoader import DocxLoader
from src.dependency import injector

manager = injector.get(ElasticManager)

def index(index_name: str, description:str, chunks:list):
    """
    Initialize an index in Elasticsearch.
    """
    manager.init_index(index_name, description)
    
    manager.bulk_index(index_name=index_name, chunks=chunks)
    
loader = DocxLoader("test_rag/tieu-su-chu-tich-ho-chi-minh_22202315.docx")
chunks = loader.chunk_text()

index_name = "hcm"
description = "tiểu sử hồ chí minh"
index(index_name,description, chunks)