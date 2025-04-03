
from uuid import UUID


class Document:
    def __init__(self, id: UUID, text:str):
        self.id = id
        self.text = text
    