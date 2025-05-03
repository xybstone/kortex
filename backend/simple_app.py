from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

# 笔记相关模型
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    user_id: Optional[int] = None
    database_ids: Optional[List[int]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    database_ids: Optional[List[int]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 数据库相关模型
class DatabaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatabaseResponse(DatabaseBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

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

# 模拟笔记数据
fake_notes_db = {
    1: {
        "id": 1,
        "title": "项目计划",
        "content": "# 项目计划\n\n这是一个项目计划文档...",
        "user_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    2: {
        "id": 2,
        "title": "会议记录",
        "content": "# 会议记录\n\n今天的会议讨论了以下内容...",
        "user_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    3: {
        "id": 3,
        "title": "学习笔记",
        "content": "# 学习笔记\n\n今天学习了以下内容...",
        "user_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

# 模拟数据库数据
fake_databases_db = {
    1: {
        "id": 1,
        "name": "项目数据",
        "description": "项目相关数据",
        "user_id": 1
    },
    2: {
        "id": 2,
        "name": "客户信息",
        "description": "客户联系信息",
        "user_id": 1
    },
    3: {
        "id": 3,
        "name": "产品目录",
        "description": "产品信息和价格",
        "user_id": 1
    }
}

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

# 笔记相关API
@app.get("/api/notes", response_model=List[NoteResponse])
async def get_notes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """获取笔记列表"""
    notes = list(fake_notes_db.values())

    # 如果提供了搜索关键词，在标题和内容中搜索
    if search:
        search = search.lower()
        notes = [
            note for note in notes
            if search in note["title"].lower() or search in note["content"].lower()
        ]

    # 分页
    start = skip
    end = skip + limit

    return notes[start:end]

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    token: str = Depends(oauth2_scheme)
):
    """获取单个笔记详情"""
    if note_id not in fake_notes_db:
        raise HTTPException(status_code=404, detail="笔记不存在")

    return fake_notes_db[note_id]

@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    token: str = Depends(oauth2_scheme)
):
    """创建新笔记"""
    # 生成新的笔记ID
    new_id = max(fake_notes_db.keys()) + 1 if fake_notes_db else 1

    # 创建新笔记
    now = datetime.now()
    new_note = {
        "id": new_id,
        "title": note.title,
        "content": note.content,
        "user_id": 1,  # 固定用户ID为1
        "created_at": now,
        "updated_at": now
    }

    # 保存到模拟数据库
    fake_notes_db[new_id] = new_note

    return new_note

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteUpdate,
    token: str = Depends(oauth2_scheme)
):
    """更新笔记"""
    if note_id not in fake_notes_db:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 获取现有笔记
    existing_note = fake_notes_db[note_id]

    # 更新笔记
    if note.title is not None:
        existing_note["title"] = note.title
    if note.content is not None:
        existing_note["content"] = note.content

    # 更新时间
    existing_note["updated_at"] = datetime.now()

    return existing_note

@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    token: str = Depends(oauth2_scheme)
):
    """删除笔记"""
    if note_id not in fake_notes_db:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 删除笔记
    del fake_notes_db[note_id]

    return None

# 数据库相关API
@app.get("/api/databases", response_model=List[DatabaseResponse])
async def get_databases(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """获取数据库列表"""
    databases = list(fake_databases_db.values())

    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        search = search.lower()
        databases = [
            db for db in databases
            if search in db["name"].lower() or (db["description"] and search in db["description"].lower())
        ]

    # 分页
    start = skip
    end = skip + limit

    return databases[start:end]
