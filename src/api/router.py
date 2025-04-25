from fastapi import  HTTPException, APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from src.api.models import  ChatRequest, ChatRequestWithInstruction
from src.utils.logger import setup_logger
from src.api.SyncWorker import SyncWorker

sync_worker = SyncWorker()
logger  = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/index")
async def index(index_name:str, description:str,file: UploadFile = File(...)):
    try:
        await sync_worker.index(file,index_name,description)
        return JSONResponse(content={"message": "Document uploaded successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = await sync_worker.chat(request)
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat_with_instruction")
async def chat_with_instruction(request: ChatRequestWithInstruction):
    try:
        answer = await sync_worker.chat_with_instruction(request)
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
