from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.endpoints import pdf
from core.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="Kortex PDF API Test",
    description="PDF转换API测试",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，仅用于测试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册PDF路由
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF处理"])

# 根路由
@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex PDF API测试服务"}

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

# 确保临时目录存在
os.makedirs("temp", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_pdf_test:app", host="0.0.0.0", port=8001, reload=True)
