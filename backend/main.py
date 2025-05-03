from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import notes, databases, llm, auth

app = FastAPI(
    title="Kortex API",
    description="API for Kortex - 在线笔记工具，支持Markdown编辑、数据库管理和大模型集成",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(notes.router, prefix="/api/notes", tags=["笔记"])
app.include_router(databases.router, prefix="/api/databases", tags=["数据库"])
app.include_router(llm.router, prefix="/api/llm", tags=["大模型"])

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
