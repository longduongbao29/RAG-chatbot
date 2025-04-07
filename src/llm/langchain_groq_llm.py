from injector import inject
from langchain_groq import ChatGroq


from src.config.config import config
from src.llm.LLM import LLM
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

class LangchainGroqLLM(LLM):
    """
    Langchain wrapper for Groq LLM.
    """
    @inject
    def __init__(self, model_name: str= None,temperature: float=None):
        self.model_name = model_name
        self.temperature = temperature
        self.config = config
        if model_name is None or temperature is None:
            self.model_name = config.MODEL_NAME
            self.temperature = config.TEMPERATURE
        self.llm = ChatGroq(api_key=config.GROQ_API_KEY,
                            model_name = self.model_name ,
                            temperature = self.temperature)
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
    def change_model(self, model_name: str, temperature: float):
        self.llm = ChatGroq(api_key=self.config.GROQ_API_KEY,
                            model_name = model_name,
                            temperature=temperature)