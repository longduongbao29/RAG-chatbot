from abc import ABC, abstractmethod
class Handler(ABC):
    def __init__(self, next_handler:"Handler"=None):
        self.next_handler = next_handler

    def handle(self, **args):
        if self.next_handler:
            return self.next_handler.handle(**args)
    def set_next(self, handler: "Handler"):
        """
        Set the next handler in the Pineline.
        """
        self.next_handler= handler
