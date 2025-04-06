import tempfile
from fastapi import  HTTPException, APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from yaml import Loader
from src.api.models import  ModelParams, Question

from src.database.ElasticManager import ElasticManager
from src.rag.strategy.chunking.loader.LoaderRouter import LoaderRouter
from src.rag.pipeline.LangGraph.Graph import Graph
from src.dependency import Dependency, injector

from src.utils.logger import setup_logger

logger  = setup_logger(__name__)

manager = injector.get(ElasticManager)
chat = injector.get(Graph)
router = APIRouter(prefix="/api")

@router.post("/index")
async def index(index_name:str, description:str,file: UploadFile = File(...)):
    try:
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

@router.post("/ask")
async def ask(question: Question):
    try:
        answer = chat.run(question.query)
        return JSONResponse(content={"answer": answer}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/change_model")
async def change_model(model: ModelParams):
    try:
        Dependency.llm.change_model(model.model_name, model.temperature)
        return JSONResponse(content={"message": "Model changed successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))