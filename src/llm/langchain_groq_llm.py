from injector import inject
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from src.config.config import Config
from src.llm.LLM import LLM
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

class LangchainGroqLLM(LLM):
    """
    Langchain wrapper for Groq LLM.
    """
    @inject
    def __init__(self,config:Config):
        self.model_name = config.MODEL_NAME
        self.temperature = config.TEMPERATURE
        self.llm = ChatGroq(api_key=config.GROQ_API_KEY,
                            model_name = config.MODEL_NAME,
                            temperature=config.TEMPERATURE)
    def generate(self, input: str,) -> str:
        """
        Generate text based on the provided prompt.
        """
        try:
            output = self.llm.invoke(input)
        except (Exception) as e:
            logger.error(f"Error in Groq LLM: {e}")
        return output.content
    def get_llm(self):
        """
        Get the LLM instance.
        """
        return self.llm
    