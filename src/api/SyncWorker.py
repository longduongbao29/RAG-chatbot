import tempfile
import asyncio

from src.api.ServicesInitiation import Provider
from src.api.models import  ChatRequest, ChatRequestWithInstruction

class SyncWorker:
    def __init__(self):
        self.provider = Provider()

    def index_(self,file_ext,content,collection_name):
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file.seek(0)
            indexer = self.provider.get_indexer()
            indexer.index_documents(temp_file.name, collection_name)
    async def index(self,file,index_name):
        file_ext = "." + file.filename.split('.')[-1].lower()
        content = await file.read()
        await asyncio.to_thread(self.index_,file_ext,content,index_name)
    def chat_(self,request: ChatRequest):
        model_name = request.model_name
        temperature = request.temperature
        use_retrieve = request.use_retrieve
        tools = request.tools
        chat_service = self.provider.get_chat(model_name, temperature, use_retrieve, tools)
        answer = chat_service.run(inputs = request.messages)
        return answer

    async def chat(self,request: ChatRequest):
        return await asyncio.to_thread(self.chat_,request)

    def chat_with_instruction_(self, request:ChatRequestWithInstruction):
        model_name = request.model_name
        temperature = request.temperature
        use_retrieve = request.use_retrieve
        instruction = request.instruction
        tools = request.tools
        chat_service = self.provider.get_chat(
            model_name,
            temperature,
            use_retrieve,
            tools,
            instruction
        )
        answer = chat_service.run(inputs = request.messages)
        return answer

    async def chat_with_instruction(self, request: ChatRequestWithInstruction):
        return await asyncio.to_thread(self.chat_with_instruction_, request)
