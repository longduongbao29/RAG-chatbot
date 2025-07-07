from langchain_core.tools.base import BaseTool
from src.llm.LLM import LLM
from src.rag.strategy.retrieval.DuckDuckGo.DuckDuckGoSearch import (
    DuckDuckGoSearchTool,
    DuckDuckGoSearch,
)
from src.utils.tools.DateTime import DateTimeTool
from src.rag.strategy.retrieval.Reranker import LLMReranker
from src.rag.strategy.retrieval.Milvus.MilvusSearch import MilvusSearchTool,MilvusSearch


class Tools:
    def __init__(self, tools: list[BaseTool]):
        self.tools = tools


class ToolManager:
    def __init__(self, tool_list: list[str], db_manager, llm:LLM):
        self.tool_list = tool_list
        self.tool_pool = {
            "milvus_search": {
                "description": "Searches the knowledge base using an elastic database. This is the default tool.",
                "instance": MilvusSearchTool(milvus_search=MilvusSearch(db_manager),reranker=LLMReranker(llm.get_llm())),
            },
            "duckduckgo_search": {
                "description": "Searches online for real-time information.",
                "instance": DuckDuckGoSearchTool(DuckDuckGoSearch()),
            },
            "datetime_tool": {
                "description": "Provides the current date and time when the query involves terms like 'today,' 'current,' 'now,' etc.",
                "instance": DateTimeTool(),
            },
        }

    def getToolDescription(self):
        description = "List tools to use:\n"
        for tool in self.tool_list:
            description += f"{tool}: {self.tool_pool[tool]['description']}\n"
        return description

    def getTools(self):
        tools = []
        for tool in self.tool_list:
            tools.append(self.tool_pool[tool]["instance"])
        return tools
