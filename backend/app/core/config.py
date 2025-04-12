# 兼容 Pydantic v1.x 和 v2.x
try:
    # Pydantic v2.x
    from pydantic_settings import BaseSettings
except ImportError:
    # Pydantic v1.x
    from pydantic import BaseSettings
from typing import Optional, Dict, Any, List


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "仓储工作流系统"

    # 数据库配置
    # 默认值适用于本地开发
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"  # 默认 PostgreSQL 端口
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "warehouse_workflow"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # 使用 SQLite 的替代配置（如果不想使用 PostgreSQL）
    # SQLALCHEMY_DATABASE_URI: str = "sqlite:///./warehouse_workflow.db"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"  # 在生产环境中应该更改
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # 允许所有来源，仅在开发环境中使用
    ]

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # RabbitMQ 配置
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    # XXL-Job 配置
    XXL_JOB_ADMIN_URL: str = "http://localhost:8080/xxl-job-admin"
    XXL_JOB_APP_NAME: str = "warehouse-workflow"
    XXL_JOB_ACCESS_TOKEN: str = ""
    XXL_JOB_ENABLE_CALLBACK: bool = True
    XXL_JOB_CALLBACK_PORT: int = 9999

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

# 如果没有显式设置数据库URI，则根据其他配置生成
if settings.SQLALCHEMY_DATABASE_URI is None:
    settings.SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
