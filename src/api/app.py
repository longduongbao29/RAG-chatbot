from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import router
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép các origins này truy cập
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, ...)
    allow_headers=["*"],  # Cho phép tất cả các headers
)

app.include_router(router)