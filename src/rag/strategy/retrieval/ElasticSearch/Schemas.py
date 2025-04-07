from pydantic import BaseModel, Field
from typing import Literal

class Index(BaseModel):
    indexs : list[str] = Field(description="list index names")