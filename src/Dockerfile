
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/src
RUN pip install hf_xet
EXPOSE 8000


CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
