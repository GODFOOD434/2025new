# Docker 服务说明

本项目使用 Docker Compose 启动所有依赖服务，包括：

- Redis：缓存和数据结构服务器
- RabbitMQ：消息队列
- XXL-Job：分布式任务调度平台
- PostgreSQL：主应用数据库

## 前提条件

- 安装 [Docker](https://www.docker.com/get-started)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

## 启动服务

### 使用脚本启动

#### Windows

```bash
start-services.bat
```

#### Linux/Mac

```bash
chmod +x start-services.sh
./start-services.sh
```

### 手动启动

1. 启动 Docker 容器

```bash
docker-compose up -d
```

2. 等待服务启动（约 30 秒）

3. 启动后端应用

```bash
cd backend
python run.py
```

## 服务访问

启动后，可以通过以下地址访问各服务：

- **Redis**：localhost:6379
- **RabbitMQ**：
  - AMQP：localhost:5672
  - 管理界面：http://localhost:15672 (用户名：guest，密码：guest)
- **XXL-Job Admin**：http://localhost:8080/xxl-job-admin (用户名：admin，密码：123456)
- **PostgreSQL**：localhost:5432 (用户名：postgres，密码：postgres，数据库：warehouse_workflow)
- **后端应用**：http://localhost:8000
- **前端应用**：http://localhost:8080 (需要单独启动)

## 停止服务

```bash
docker-compose down
```

## 查看日志

```bash
# 查看所有容器日志
docker-compose logs

# 查看特定服务日志
docker-compose logs redis
docker-compose logs rabbitmq
docker-compose logs xxl-job-admin
docker-compose logs postgres
```

## 数据持久化

所有服务的数据都通过 Docker 卷进行持久化，即使容器重启或删除，数据也不会丢失。

卷列表：
- redis-data
- rabbitmq-data
- xxl-job-db-data
- postgres-data

## 注意事项

1. 首次启动时，XXL-Job Admin 可能需要一些时间初始化数据库，请耐心等待。

2. 如果遇到端口冲突，可以在 docker-compose.yml 文件中修改端口映射。

3. 在生产环境中，建议修改默认密码和增加安全配置。
