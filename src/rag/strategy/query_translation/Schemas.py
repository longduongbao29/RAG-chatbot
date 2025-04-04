from pydantic import BaseModel, Field

class Query(BaseModel):
    """
    Query object for RAG Fusion.
    """
    queries: list[str] = Field(..., description="The query string to etracted.")
    