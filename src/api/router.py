import tempfile
from fastapi import  HTTPException, APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from src.api.models import  ChatRequest
from src.rag.strategy.chunking.loader.LoaderRouter import LoaderRouter

from src.api.ServiceDispatcher import ChatServiceProvider, ElasticManagerProvider
from src.utils.logger import setup_logger

logger  = setup_logger(__name__)

chat_provider = ChatServiceProvider()
router = APIRouter(prefix="/api", tags=["api"])

@router.post("/index")
async def index(index_name:str, description:str,file: UploadFile = File(...)):
    try:
        manager = ElasticManagerProvider().create()
        file_ext = "." + file.filename.split('.')[-1].lower()
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as temp_file:
            temp_file.write(await file.read())
            temp_file.seek(0)
            temp_file_path = temp_file.name
            loader = LoaderRouter(temp_file_path).router()
            chunks = loader.chunk_text()
            manager.init_index(index_name, description)
            manager.bulk_index(index_name=index_name, chunks=chunks)
            return JSONResponse(content={"message": "Document uploaded successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def ask(request: ChatRequest):
    try:
        model_name = request.model_name
        temperature = request.temperature
        db_manager = ElasticManagerProvider().create()
        chat_service = chat_provider.dispatch(model_name,temperature, db_manager)
        
        chat = chat_service.service
        answer = chat.run(request.messages)
        
        chat_provider.recall(chat_service)
        
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
