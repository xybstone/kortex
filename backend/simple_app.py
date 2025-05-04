from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

# 导入数据库相关模块
from database.session import SessionLocal, engine
from models.simple_models import User as DBUser, Note as DBNote, Database as DBDatabase
from core.config import settings

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 数据库依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 密码验证和哈希函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

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

# JWT令牌相关函数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# 认证相关
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 获取当前用户依赖项
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    # 查询用户
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()

    # 验证用户和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        # 如果用户不存在或密码不正确，返回错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已被注册
    db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_admin=False
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "注册成功"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: DBUser = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin
    }

# 初始化数据库表
# 注意：在生产环境中，应该使用Alembic进行数据库迁移
# 这里为了简单起见，直接创建表
from models.simple_models import Base
Base.metadata.create_all(bind=engine)

# 创建初始用户
def init_db():
    db = SessionLocal()
    try:
        # 检查是否已存在用户
        user = db.query(DBUser).filter(DBUser.email == "user@example.com").first()
        if not user:
            # 创建默认用户
            hashed_password = get_password_hash("password")
            default_user = DBUser(
                email="user@example.com",
                full_name="测试用户",
                hashed_password=hashed_password,
                is_active=True,
                is_admin=False
            )
            db.add(default_user)
            db.commit()
            print("已创建默认用户: user@example.com")
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
    finally:
        db.close()

# 初始化数据库
init_db()

@app.get("/")
async def root():
    return {"message": "欢迎使用Kortex API"}

# 笔记相关API
@app.get("/api/notes", response_model=List[NoteResponse])
async def get_notes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取笔记列表"""
    # 构建查询
    query = db.query(DBNote).filter(DBNote.user_id == current_user.id)

    # 如果提供了搜索关键词，在标题和内容中搜索
    if search:
        search = f"%{search}%"
        query = query.filter(
            (DBNote.title.ilike(search)) | (DBNote.content.ilike(search))
        )

    # 分页
    notes = query.order_by(DBNote.created_at.desc()).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
        for note in notes
    ]

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个笔记详情"""
    # 查询笔记
    note = db.query(DBNote).filter(
        DBNote.id == note_id,
        DBNote.user_id == current_user.id
    ).first()

    # 检查笔记是否存在
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }

@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新笔记"""
    # 创建新笔记
    db_note = DBNote(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )

    # 保存到数据库
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return {
        "id": db_note.id,
        "title": db_note.title,
        "content": db_note.content,
        "user_id": db_note.user_id,
        "created_at": db_note.created_at,
        "updated_at": db_note.updated_at
    }

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新笔记"""
    # 查询笔记
    db_note = db.query(DBNote).filter(
        DBNote.id == note_id,
        DBNote.user_id == current_user.id
    ).first()

    # 检查笔记是否存在
    if not db_note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 更新笔记
    if note.title is not None:
        db_note.title = note.title
    if note.content is not None:
        db_note.content = note.content

    # 保存更新
    db.commit()
    db.refresh(db_note)

    return {
        "id": db_note.id,
        "title": db_note.title,
        "content": db_note.content,
        "user_id": db_note.user_id,
        "created_at": db_note.created_at,
        "updated_at": db_note.updated_at
    }

@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除笔记"""
    # 查询笔记
    db_note = db.query(DBNote).filter(
        DBNote.id == note_id,
        DBNote.user_id == current_user.id
    ).first()

    # 检查笔记是否存在
    if not db_note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    # 删除笔记
    db.delete(db_note)
    db.commit()

    return None

# 数据库相关API
@app.get("/api/databases", response_model=List[DatabaseResponse])
async def get_databases(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取数据库列表"""
    # 构建查询
    query = db.query(DBDatabase).filter(DBDatabase.user_id == current_user.id)

    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        search = f"%{search}%"
        query = query.filter(
            (DBDatabase.name.ilike(search)) |
            (DBDatabase.description.ilike(search))
        )

    # 分页
    databases = query.order_by(DBDatabase.name).offset(skip).limit(limit).all()

    # 转换为响应模型
    return [
        {
            "id": database.id,
            "name": database.name,
            "description": database.description,
            "user_id": database.user_id
        }
        for database in databases
    ]
