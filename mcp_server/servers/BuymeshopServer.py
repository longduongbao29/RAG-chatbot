from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from elasticsearch import Elasticsearch

mcp = FastMCP("Elasticsearch MCP server")

def connect_db(es_host='localhost', es_port=9200):
    """
    Connect to Elasticsearch.
    """
    es_manager = Elasticsearch([{'host': es_host, 'port': es_port}])
    return es_manager
@mcp.tool
def search(keyword: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        brand: Optional[str] = None, 
        description: Optional[str] = None,
        size: int = 10,
        from_: int = 0) -> List[Dict[str, Any]]:
    """
    Search and filter products from Elasticsearch.
    """
    return [{
        "keyword": keyword,
        "min_price": min_price,
        "max_price": max_price,
        "brand": brand,
        "description": description,
        "size": size,
        "from": from_
    }]
    must_clauses = []
    filter_clauses = []

    if keyword:
        must_clauses.append({
            "multi_match": {
                "query": keyword,
                "fields": ["name^2", "description", "brand"]
            }
        })
    if description:
        must_clauses.append({
            "match": {
                "description": description
            }
        })
    if brand:
        filter_clauses.append({
            "term": {
                "brand.keyword": brand
            }
        })
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        filter_clauses.append({
            "range": {
                "price": price_range
            }
        })

    query = {
        "query": {
            "bool": {
                "must": must_clauses if must_clauses else {"match_all": {}},
                "filter": filter_clauses
            }
        },
        "from": from_,
        "size": size
    }

    results = self.es_manager.search(self.index_name, query)
    return [hit["_source"] for hit in results]

if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="streamable-http", host="localhost", port=8001)