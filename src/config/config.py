import os
from tkinter import E


class Config():
    
    #ELASTIC
    ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY","")
    ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT","https://localhost:9200")
    ELASTIC_CERT_PATH = os.getenv("ELASTIC_CERT_PATH","")
    ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME","elastic")
    ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD","")
    
    #GROQ
    GROQ_API_KEY = os.getenv("GROQ_API_KEY","")
    MODEL_NAME = os.getenv("MODEL_NAME","llama-3.3-70b-versatile")
    TEMPERATURE = os.getenv("TEMPERATURE",0.5)