
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import DuckDuckGoSearch


search = DuckDuckGoSearch()
print(search.retrieve("Thời tiết hôm nay tại hà nội"))