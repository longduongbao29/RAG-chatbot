from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum
# Model cho tài liệu
class Document(BaseModel):
    title: str
    content: str

# Model cho câu hỏi
class Question(BaseModel):
    query: str


class Tool(str,Enum):
    MILVUS_SEARCH = "milvus_search"
    DUCKDUCKGO_SEARCH = "duckduckgo_search"
    DATETIME_TOOL = "datetime_tool"
class RagStrategy(str,Enum):
    SELF_RAG = "self_rag"
    C_RAG = "c_rag"
    NO_RAG = "no_rag"
class ChatRequest(BaseModel):
    session_id : str
    rag_strategy : str = Field(default = "no_rag")
    messages: list = Field(
        ...,
        example=[
            {"role": "user", "message": "Hello, how are you?"},
            {"role": "AI", "message": "I'm good, thank you! How can I assist you today?"}
        ]
    )
    provider : Literal["groq", "openai"]
    model_name: str
    temperature: float

class ChatRequestWithInstruction(ChatRequest):
    instruction: str = Field(description="Instruction for chatbot agent")
