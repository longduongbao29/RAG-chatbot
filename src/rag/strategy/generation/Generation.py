from langchain_core.prompts import PromptTemplate

from injector import inject

from src.llm.LLM import LLM
from src.rag.strategy.generation.Prompt import GEN_PROMPT_TEMPLATE
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

class LLMGenerator:
    """
    Class to handle the generation of text using a language model.
    """
    @inject
    def __init__(self, llm: LLM):
        self.llm = llm.get_llm()
        self.prompt = GEN_PROMPT_TEMPLATE
    
    def generate(self, query: str, context: str = "") -> str:
        """
        Generate text based on the provided query.
        """
        
        try:
            chain = self.prompt|self.llm
            output =chain.invoke({"query": query, "context": context})
        except Exception as e:
            logger.error(f"Error in LLM generation: {e}")
            return None
        return output.content