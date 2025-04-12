# 仓储工作流系统 - 后端

这是仓储工作流系统的后端部分，使用 FastAPI 框架开发。

## 功能

- 采购订单管理
- 工作流处理
- 确认单管理
- 出库管理
- 库存管理
- 用户管理
- 报表生成

## 技术栈

- FastAPI：Web 框架
- SQLAlchemy：ORM
- PostgreSQL：数据库
- Pydantic：数据验证
- JWT：身份验证

## 安装

### 自动安装（推荐）

#### Windows

```bash
install.bat
```

#### Linux/Mac

```bash
chmod +x install.sh
./install.sh
```

### 手动安装

1. 创建虚拟环境：

```bash
python -m venv venv
```

2. 激活虚拟环境：

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -e .
```

> 注意：对于 Python 3.13 用户，我们使用 polars 替代 pandas，因为 pandas 与 Python 3.13 的兼容性存在问题。

4. 创建 `.env` 文件（在项目根目录），并设置以下环境变量：

```
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=warehouse_workflow

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 天

# CORS配置
BACKEND_CORS_ORIGINS=["*"]
```

## 运行

```bash
python run.py
```

服务器将在 http://localhost:8000 上运行。

## API 文档

启动服务器后，可以在以下地址查看 API 文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 测试

```bash
pytest
```
