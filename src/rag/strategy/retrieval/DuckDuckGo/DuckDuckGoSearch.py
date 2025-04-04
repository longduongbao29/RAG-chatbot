from langchain_community.tools import DuckDuckGoSearchRun

from src.rag.strategy.retrieval.OnlineSearch import OnlineSearch


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