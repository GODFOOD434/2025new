from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.json_encoder import CustomJSONEncoder

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=JSONResponse
)

# 配置自定义JSON编码器
app.json_encoder = CustomJSONEncoder

# 设置CORS
# 对于开发环境，我们使用更宽松的 CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，仅在开发环境中使用
    allow_credentials=False,  # 当使用 allow_origins=["*"] 时，必须设置为 False
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "欢迎使用仓储工作流系统API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
