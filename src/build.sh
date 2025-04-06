#!/bin/bash

# Lấy thời gian hiện tại theo định dạng "YYYY-MM-DD-HHMMSS" để gắn tag
TIMESTAMP=$(date +'%Y-%m-%d')

# Tên image của bạn
IMAGE_NAME="rag_chatbot"

docker build -t ${IMAGE_NAME}:${TIMESTAMP} .

# In ra thông tin image đã tạo
echo "✅Docker image ${IMAGE_NAME}:${TIMESTAMP} đã được tạo."


