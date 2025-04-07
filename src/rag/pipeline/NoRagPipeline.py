
from langchain_core.prompts import ChatPromptTemplate

from src.llm.LLM import LLM
from src.llm.Schemas import LLMParams
from src.rag.pipeline.ChatPipeline import ChatPipeline
from src.llm.Provider import LLMProvider
from src.utils.logger import setup_logger
from src.utils.helpers import format_history

PROMPT = ChatPromptTemplate([
    ("system", "You are a helpful AI bot."),
    ("human", "History chat: {history}\nUser: {user_input}"),
])


logger = setup_logger(__name__)
class NoRagPipeline(ChatPipeline):
    
    def __init__(self, llm_params:LLMParams):
        super().__init__()
        self.llm_params = llm_params
        self.llm = LLMProvider(llm_params).provide_llm()
    def run(self, record_chat:list):
        logger.info("Running NoRagPipeline")
        user_input = record_chat[-1]
        history = format_history(record_chat)
        chain = PROMPT|self.llm.get_llm()
        answer = chain.invoke({"user_input": user_input, "history": history})
        content = LLM.postprocess(answer.content)
        return content