from pydantic import BaseModel, Field
from typing import Literal

class Index(BaseModel):
    index_name : str = Field(description="index name")