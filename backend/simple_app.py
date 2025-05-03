from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟用户数据
fake_users_db = {
    "user@example.com": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "测试用户",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "is_active": True,
        "is_admin": False
    }
}

# 模型定义
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

# 认证相关
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 简单模拟登录，不验证密码
    user = fake_users_db.get(form_data.username)
    if not user:
        # 如果用户不存在，自动创建一个
        user_id = len(fake_users_db) + 1
        fake_users_db[form_data.username] = {
            "id": user_id,
            "email": form_data.username,
            "full_name": None,
            "hashed_password": "fake_hashed_password",
            "is_active": True,
            "is_admin": False
        }

    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE4MzgwODAwfQ.8H7MnKTCZl4L6ICv8cj8O9K9l1fU1TEyQ7QgQxpLNSo",
        "token_type": "bearer"
    }

@app.post("/api/auth/register")
async def register(user: UserCreate):
    # 简单模拟注册，不验证邮箱是否已存在
    user_id = len(fake_users_db) + 1
    fake_users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": "fake_hashed_password",
        "is_active": True,
        "is_admin": False
    }
    return {"message": "注册成功"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 简单模拟返回用户信息，不验证token
    # 在实际应用中，应该从token中解析用户信息
    print(f"接收到的token: {token}")
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "测试用户",
        "is_active": True,
        "is_admin": False
    }

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}
