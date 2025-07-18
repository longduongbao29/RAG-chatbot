from langchain_groq import ChatGroq
from langchain_openai.chat_models import ChatOpenAI

from src.config.config import config
from src.llm.Schemas import LLMParams

class LLMProvider:
    def __init__(self, llm_params: LLMParams):
        self.llm_params = llm_params
    def provide_llm(self):
        if self.llm_params.provider == "groq":
            return ChatGroq(api_key=config.GROQ_API_KEY,
                            model= self.llm_params.model_name,
                            temperature = float(self.llm_params.temperature))
        elif self.llm_params.provider == "openai":
            return ChatOpenAI(api_key=config.OPENAI_API_KEY,
                              model= self.llm_params.model_name,
                              temperature = float(self.llm_params.temperature))
        else:
            raise ValueError("At "+__name__+":provider name invalid!")