from langchain_core.tools.base import BaseTool

class Tools:
    def __init__(self, tools:list[BaseTool]):
        self.tools = tools