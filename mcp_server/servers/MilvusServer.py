from os import name
from fastmcp import FastMCP
from typing import List, Dict, Any
from pymilvus import connections
mcp = FastMCP("Milvus MCP server")

def connect_db(milvus_host='localhost', milvus_port=19530):
    """
    Connect to Milvus.
    """
    connections.connect(host=milvus_host, port=milvus_port)
    return connections
@mcp.tool
def search(collection_name: str,
           query: str,
           limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search and filter products from Milvus.
    """
    if not connections.has_connection("default"):
        connect_db()

    return [{"collection": collection_name, "query": query, "limit": limit}]
    # collection = Collection(name=collection_name)
    
    # results = collection.query(expr=query, limit=limit)
    
    # return [{"id": result.id, "data": result} for result in results]    

if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="streamable-http", host="localhost", port=8002)