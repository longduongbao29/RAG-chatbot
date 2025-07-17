import tempfile
import asyncio

from src.api.ServicesInitiation import Provider
from src.api.models import  ChatRequest, ChatRequestWithInstruction
from src.utils.helpers import session2collection

class SyncWorker:
    def __init__(self):
        self.provider = Provider()

    def index(self,session_id,file_ext,content):
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file.seek(0)
            indexer = self.provider.get_indexer(session_id)
            indexer.index_documents(temp_file.name)
    async def aindex(self,session_id,file):
        file_ext = "." + file.filename.split('.')[-1].lower()
        content = await file.read()
        await asyncio.to_thread(self.index,session_id,file_ext,content)
    def chat(self,request: ChatRequest):
        chat_service = self.provider.get_chat(session_id = request.session_id,
                                              provider = request.provider,
                                              model_name = request.model_name, 
                                              temperature = request.temperature, 
                                              rag_strategy = request.rag_strategy)
        answer = chat_service.run(inputs = request.messages)
        return answer

    async def achat(self,request: ChatRequest):
        return await asyncio.to_thread(self.chat,request)

    def chat_with_instruction(self, request:ChatRequestWithInstruction):
        model_name = request.model_name
        temperature = request.temperature
        instruction = request.instruction
        chat_service = self.provider.get_chat(
            model_name,
            temperature,
            instruction
        )
        answer = chat_service.run(inputs = request.messages)
        return answer

    async def achat_with_instruction(self, request: ChatRequestWithInstruction):
        return await asyncio.to_thread(self.chat_with_instruction, request)
    
    def create_session(self, session_id):
        self.provider.db_manager.create_collection(session2collection(session=session_id))

    async def acreate_session(self,session_id):
        return await asyncio.to_thread(self.create_session, session_id)
    
    def delete_session(self, session_id):
        self.provider.db_manager.delete_collection(session2collection(session=session_id))
    async def adelete_session(self, session_id):
        return await asyncio.to_thread(self.delete_session, session_id)