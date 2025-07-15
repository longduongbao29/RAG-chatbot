from abc import ABC, abstractmethod

class ChatPipeline(ABC):
    @abstractmethod
    def run(self):
        pass