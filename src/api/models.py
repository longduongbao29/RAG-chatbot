from pydantic import BaseModel
from typing import Optional

# Model cho tài liệu
class Document(BaseModel):
    title: str
    content: str

# Model cho câu hỏi
class Question(BaseModel):
    query: str
