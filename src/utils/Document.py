

class Document:
    def __init__(self, id: str, content:str, score: float = 0.0):
        self.id = id
        self.content = content
        self.score = score
    