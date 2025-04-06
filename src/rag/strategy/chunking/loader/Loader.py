
from abc import ABC, abstractmethod

class Loader(ABC):
    
    @abstractmethod
    def load():
        pass
        
    @abstractmethod
    def chunk_text():
        pass
    
  