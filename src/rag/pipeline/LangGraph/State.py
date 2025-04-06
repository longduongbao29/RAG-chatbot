from typing_extensions import TypedDict
from typing import Annotated


class State(TypedDict):
    query: str
    translated_queries: list[str] 
    tools : list
    context: str 
    messages: list[dict]
    decision: str