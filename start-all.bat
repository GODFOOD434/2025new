@echo off
echo 启动所有服务...

echo 启动 Docker 容器...
docker-compose up -d

echo 等待服务启动...
timeout /t 10

echo 启动后端应用...
start cmd /k "cd backend && python run.py"

echo 等待后端启动...
timeout /t 5

echo 启动前端应用...
start cmd /k "cd frontend && npm run serve"

echo 所有服务已启动！
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:8080
echo API 文档: http://localhost:8000/docs
