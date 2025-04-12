# 前后端连接说明

本项目由前端（Vue.js）和后端（FastAPI）两部分组成，通过 API 进行通信。

## 项目结构

- **前端**：`C:\Users\A\Desktop\base\2025new\frontend`
- **后端**：`C:\Users\A\Desktop\base\2025new\backend`

## 连接机制

前端通过 HTTP 请求与后端 API 通信。连接机制如下：

1. **前端代理配置**：
   - 前端开发服务器配置了代理，将 `/api` 请求转发到 `http://localhost:8000/api/v1`
   - 配置文件：`frontend/vue.config.js`

2. **后端 CORS 配置**：
   - 后端允许跨域请求，支持前端直接访问 API
   - 配置文件：`backend/.env` 中的 `BACKEND_CORS_ORIGINS=["*"]`

3. **API 请求**：
   - 前端使用 Axios 发送 API 请求
   - 请求工具：`frontend/src/utils/request.js`

## 启动项目

### 方法一：使用启动脚本（推荐）

使用提供的启动脚本可以一键启动所有服务：

#### Windows

```bash
start-all.bat
```

#### Linux/macOS

```bash
chmod +x start-all.sh
./start-all.sh
```

### 方法二：分别启动

#### 1. 启动 Docker 服务

```bash
docker-compose up -d
```

#### 2. 启动后端

```bash
cd backend
python run.py
```

#### 3. 启动前端

```bash
cd frontend
npm run serve
```

## 访问地址

- **前端**：http://localhost:8080
- **后端 API**：http://localhost:8000/api/v1
- **API 文档**：http://localhost:8000/docs

## 开发模式

### 前端开发

前端使用 Vue.js 框架，主要文件：

- **API 请求**：`src/utils/request.js` 和 `src/api/index.js`
- **路由配置**：`src/router/index.js`
- **状态管理**：`src/store/index.js`
- **组件**：`src/components/`
- **视图**：`src/views/`

### 后端开发

后端使用 FastAPI 框架，主要文件：

- **API 路由**：`app/api/api_v1/endpoints/`
- **数据模型**：`app/models/`
- **数据库**：`app/db/`
- **业务逻辑**：`app/services/`

## 模拟数据模式

前端支持模拟数据模式，可以在不连接后端的情况下进行开发：

- 配置文件：`src/utils/request.js` 中的 `MOCK_MODE` 变量
- 设置为 `true` 启用模拟数据，设置为 `false` 使用真实后端 API

## 故障排除

### 跨域问题

如果遇到跨域问题，请检查：

1. 后端 CORS 配置是否正确
2. 前端代理配置是否正确
3. 请求 URL 是否正确（应以 `/api` 开头）

### 连接问题

如果前端无法连接到后端，请检查：

1. 后端服务是否正在运行
2. 端口是否正确（后端默认为 8000）
3. 网络连接是否正常

### 认证问题

如果遇到认证问题，请检查：

1. 前端是否正确发送 Authorization 头
2. 后端是否正确验证 token
3. token 是否过期
