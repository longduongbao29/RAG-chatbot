import ast
import re
from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel

class LLM(ABC):
    """
    Abstract base class for Language Models (LLMs).
    """
    model_name:str
    temperature:float
    @abstractmethod
    def generate(self) -> str:
        """
        Generate text based on the provided prompt.
        """
        pass
    @abstractmethod
    def get_llm(self)->BaseChatModel:
        """
        Get the LLM instance.
        """
        pass
    @classmethod
    def remove_think_tags(cls,input_string:str):
        """
        Removes content within <think>...</think> tags from the input string.

        Args:
            input_string (str): The input string to process.

        Returns:
            str: The processed string with <think>...</think> content removed.
        """
        # Use regex to find and remove <think>...</think> and its content
        return re.sub(r'<think>.*?</think>', '', input_string, flags=re.DOTALL).lstrip('\n')

    @classmethod
    def postprocess(cls,input_string:str):
        """
        Removes content within <think>...</think> tags from the input string.

        Args:
            input_string (str): The input string to process.

        Returns:
            str: The processed string with <think>...</think> content removed.
        """
        output = cls.remove_think_tags(input_string)
        try:
            output = ast.literal_eval(output)
            output = output["message"]
        except:
            pass
        return output