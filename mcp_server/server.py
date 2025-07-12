# server.py
from mcp.server.fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun

# Create an MCP server
mcp = FastMCP("Chatbot")


# Add an addition tool
@mcp.tool()
def duck_duck_go(query: str) -> str:
    """
    Search DuckDuckGo for a query.
    """
    return DuckDuckGoSearchRun().invoke(query)

@mcp.tool()
def milvus_search(query: str) -> str:
    """
    Search Milvus for a query.
    """
    # Placeholder for Milvus search logic
    return f"Search results for '{query}' from Milvus."

if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="stdio")