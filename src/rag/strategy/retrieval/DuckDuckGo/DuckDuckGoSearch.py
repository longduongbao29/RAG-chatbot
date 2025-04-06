from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools.base import BaseTool
from src.rag.strategy.retrieval.OnlineSearch import OnlineSearch

from src.utils.logger import setup_logger
logger= setup_logger(__name__)
class DuckDuckGoSearch(OnlineSearch):
    def __init__(self):
        """
        Initialize the DuckDuckGoSearch class.
        """
        self.tool = DuckDuckGoSearchRun()
    def search(self, query: str):
        """
        Perform a search using DuckDuckGo.
        """
        results = self.tool.invoke(query)
        return results
    def retrieve(self, query:str):
        return [self.search(query)]
class DuckDuckGoSearchTool(BaseTool):
    name:str = "duckduckgo_search"
    description:str = (
        "A wrapper around DuckDuckGo Search. "
        "Useful for when you need to answer questions about current events, search for information on the internet. "
        "Input should be a search query."
    )
    duckduckgo_search:DuckDuckGoSearchRun = None
    def __init__(self, duckduckgo_search: DuckDuckGoSearch):
        """
        Initialize the DuckDuckGoSearchTool class.
        """
        super().__init__()
        self.duckduckgo_search = duckduckgo_search.tool
    def _run(self, **args) -> str:
        query: str = args["query"]
        context = args["context"]
        translated_queries:list = args["translated_queries"]
        queries:list = [query] + translated_queries + [context] 
        searching_query = "\n".join(queries)
        
        try:
            result= self.duckduckgo_search.invoke(searching_query)
        except Exception as e:
            result = "" 
        return result