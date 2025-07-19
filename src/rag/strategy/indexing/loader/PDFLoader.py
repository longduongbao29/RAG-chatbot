import os
from PyPDF2 import PdfReader

from src.rag.strategy.indexing.loader.Loader import Loader

class PDFLoader(Loader):
    def __init__(self, file_path: str, chunk_size: int = 1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.text = ''
        self.load()
    def load(self) :
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        pdf_reader = PdfReader(self.file_path)
        for page in pdf_reader.pages:
            self.text += page.extract_text() + "\n"

