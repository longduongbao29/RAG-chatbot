from src.config.config import config
from src.llm.Schemas import LLMParams
from src.llm.langchain_groq_llm import LangchainGroqLLM
class LLMProvider:
    def __init__(self, llm_params: LLMParams):
        self.llm_params = llm_params
    def provide_llm(self):
        if self.llm_params.provider == "groq":
            return LangchainGroqLLM(model_name=self.llm_params.model_name,temperature=self.llm_params.temperature)
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_params.provider}")