
import os

from src.rag.strategy.indexing.loader.Loader import Loader

class DocxLoader(Loader):
    def __init__(self, file_path: str, chunk_size: int = 1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.text = ''
        self.doc = self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.text = "\n".join([paragraph.text for paragraph in self.doc.paragraphs])

