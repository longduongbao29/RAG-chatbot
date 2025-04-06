from src.rag.strategy.retrieval.ElasticSearch.ElasticVectorSearch import ElasticSearchTool

from src.dependency import injector 

tool = injector.get(ElasticSearchTool)

print(tool.get_descriptions())