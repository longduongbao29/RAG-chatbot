from fastapi import  HTTPException, APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from src.api.models import  ChatRequest, ChatRequestWithInstruction
from src.utils.logger import setup_logger
from src.api.SyncWorker import SyncWorker

sync_worker = SyncWorker()
logger  = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/upload")
async def upload(session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        await sync_worker.aindex(session_id,file)
        return JSONResponse(content={"message": "Document uploaded successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = await sync_worker.achat(request)
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat_with_instruction")
async def chat_with_instruction(request: ChatRequestWithInstruction):
    try:
        answer = await sync_worker.achat_with_instruction(request)
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/create_session/{session_id}")
async def create_session(session_id:str):
    try:
        await sync_worker.acreate_session(session_id = session_id)
        return JSONResponse(content={"message": f"New session {session_id} created"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_session/{session_id}")
async def delete_session(session_id:str):
    try:
        await sync_worker.adelete_session(session_id = session_id)
        return JSONResponse(content={"message": f"Session {session_id} deleted!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
