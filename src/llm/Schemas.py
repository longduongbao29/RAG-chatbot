from pydantic import BaseModel, Field

class LLMParams(BaseModel):
    model_name: str
    temperature: float
    provider: str = Field(
        default="groq",
    )