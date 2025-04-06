
import os
from typing import List, Dict
from PyPDF2 import PdfReader
from src.rag.strategy.chunking.loader.Loader import Loader

class PDFLoader(Loader):
    def __init__(self, file_path: str, chunk_size: int = 1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.pdf_reader = self.load()

    def load(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        return PdfReader(self.file_path)

    def chunk_text(self) -> List[str]:
        text = ""
        for page in self.pdf_reader.pages:
            text += page.extract_text() + "\n"
        chunks = []
        current_chunk = ""

        for paragraph in text.split("\n"):
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += " " + paragraph if current_chunk else paragraph

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks