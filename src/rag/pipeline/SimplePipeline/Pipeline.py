
from src.dependency import injector

from src.rag.pipeline.SimplePipeline.Handler import Handler
from src.rag.pipeline.SimplePipeline.QueryTranslationHandler import QueryTranslationHandler
from src.rag.pipeline.SimplePipeline.RetrievalHandler import RetrievalHandler
from src.rag.pipeline.SimplePipeline.GenerationHandler import GenerationHandler

class Pipeline:
        
    def run_pipeline(self, query: str,index_name: str):

        query_translation_handler = injector.get(QueryTranslationHandler)
        retrieval_handler = injector.get(RetrievalHandler)
        retrieval_handler.set_index_name(index_name)
        generation_handler = injector.get(GenerationHandler)
        
        query_translation_handler.set_next(retrieval_handler)
        retrieval_handler.set_next(generation_handler)
        
        start = Handler(query_translation_handler)
        
        return start.handle(query=query)
        