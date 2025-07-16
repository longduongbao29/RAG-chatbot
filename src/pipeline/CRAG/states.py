from typing import List

from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        conversation: conversation
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    conversation: List
    generation: str
    web_search: str
    documents: List[str]