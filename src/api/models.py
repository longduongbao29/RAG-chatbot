from pydantic import BaseModel, Field
from enum import Enum
# Model cho tài liệu
class Document(BaseModel):
    title: str
    content: str

# Model cho câu hỏi
class Question(BaseModel):
    query: str


class Tool(str,Enum):
    ELASTIC_SEARCH = "elastic_search"
    DUCKDUCKGO_SEARCH = "duckduckgo_search"
    DATETIME_TOOL = "datetime_tool"
class ChatRequest(BaseModel):
    use_retrieve: bool = Field(default=False)
    tools: list[Tool]
    messages: list = Field(
        ...,
        example=[
            {"role": "user", "message": "Hello, how are you?"},
            {"role": "AI", "message": "I'm good, thank you! How can I assist you today?"}
        ]
    )
    model_name: str
    temperature: float

class ChatRequestWithInstruction(ChatRequest):
    instruction: str = Field(description="Instruction for chatbot agent")
