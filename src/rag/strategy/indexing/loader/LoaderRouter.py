from src.rag.strategy.indexing.loader.PDFLoader import PDFLoader
from src.rag.strategy.indexing.loader.DocxLoader import DocxLoader

class LoaderRouter:
    def __init__(self, file_path: str, chunk_size: int = 1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
    def router(self):
        if self.file_path.endswith(".pdf"):
            return PDFLoader(self.file_path, self.chunk_size)
        elif self.file_path.endswith(".docx"):
            return DocxLoader(self.file_path, self.chunk_size)
        else:
            raise ValueError("Unsupported file format")