#!/bin/bash
echo "启动所有服务..."

echo "启动 Docker 容器..."
docker-compose up -d

echo "等待服务启动..."
sleep 30

echo "启动后端应用..."
cd backend
python run.py
