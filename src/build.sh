#!/bin/bash

# Lấy thời gian hiện tại theo định dạng "YYYY-MM-DD-HHMMSS" để gắn tag
TIMESTAMP=$(date +'%Y-%m-%d')

# Tên image của bạn
IMAGE_NAME="chatbot_backend"

docker build -t ${IMAGE_NAME}:latest .

# In ra thông tin image đã tạo
echo "✅Docker image ${IMAGE_NAME}:latest đã được tạo."


