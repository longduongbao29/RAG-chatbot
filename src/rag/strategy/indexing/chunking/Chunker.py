from abc import ABC, abstractmethod
from re import split

from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from src.utils.Document import Document


class Chunker(ABC):
    """
    Abstract base class for chunkers.
    """
    def __init__(self):
        """
        Initialize the chunker.
        """

    @classmethod
    def default_chunk_text(cls,text: str) -> list[Document]:
        """
        Return the default chunker instance.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".",]
        )
        chunks = splitter.split_text(text)
        documents = [Document(id=str(i), content=chunk) for i, chunk in enumerate(chunks)]
        return documents
    
    @abstractmethod
    def chunk_text(self, text: str) -> list[Document]:
        """
        Chunk the input text into smaller segments.
        """
        pass