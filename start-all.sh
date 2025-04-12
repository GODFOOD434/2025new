#!/bin/bash
echo "启动所有服务..."

echo "启动 Docker 容器..."
docker-compose up -d

echo "等待服务启动..."
sleep 10

echo "启动后端应用..."
cd backend && python run.py &
BACKEND_PID=$!

echo "等待后端启动..."
sleep 5

echo "启动前端应用..."
cd frontend && npm run serve &
FRONTEND_PID=$!

echo "所有服务已启动！"
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:8080"
echo "API 文档: http://localhost:8000/docs"

# 等待用户按 Ctrl+C
echo "按 Ctrl+C 停止所有服务"
wait $BACKEND_PID $FRONTEND_PID
