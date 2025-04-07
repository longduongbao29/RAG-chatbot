import tempfile
import asyncio

from src.api.InitServices import Provider
from src.rag.strategy.chunking.loader.LoaderRouter import LoaderRouter
from src.api.models import  ChatRequest
class SyncWorker:
    def __init__(self):
        self.provider = Provider()
        self.manager = self.provider.get_db_manager()
        
    def index_(self,file_ext,content,index_name,description):
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file.seek(0)
            temp_file_path = temp_file.name
            loader = LoaderRouter(temp_file_path).router()
            chunks = loader.chunk_text()
            self.manager.init_index(index_name, description)
            self.manager.bulk_index(index_name=index_name, chunks=chunks)
    async def index(self,file_ext,file,index_name,description):
        file_ext = "." + file.filename.split('.')[-1].lower()
        content = await file.read()
        await asyncio.to_thread(self.index_,file_ext,content,index_name,description)
    def chat_(self,request: ChatRequest):
        model_name = request.model_name
        temperature = request.temperature
        chat_service = self.provider.get_chat(model_name, temperature)
        answer = chat_service.run(request.messages)
        return answer
    
    async def chat(self,request: ChatRequest):
        return await asyncio.to_thread(self.chat_,request)