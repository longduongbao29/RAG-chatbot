from pydantic import BaseModel, Field
from typing import Literal

class AnalyzedTools(BaseModel):
    """
    Analyzed tools for the LangGraph pipeline.
    """

    tools: list[str] = Field(
        description="List of tools to be analyzed by the LangGraph pipeline.",
    )
class Decision(BaseModel):
    """
    Decision made by the LangGraph pipeline.
    """

    decision: Literal["retrieve", "answer"] = Field(
        description="Decision made by the LangGraph pipeline. Must be 'retrieve' or 'answer'."
    )