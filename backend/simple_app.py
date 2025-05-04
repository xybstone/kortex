from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

# 导入数据库相关模块
from database.session import SessionLocal, engine
from models.simple_models import User as DBUser, SimpleNote as DBNote, Database as DBDatabase
from core.config import settings

# 导入LLM相关模块
print("警告：无法导入LLM模块，将使用模拟数据")

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册LLM路由
# 暂时注释掉，避免错误
# try:
#     app.include_router(llm.router, prefix="/api/llm", tags=["大模型"])
#     print("已成功注册LLM路由")
# except Exception as e:
#     print(f"注册LLM路由失败: {e}")

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
try:
    from models.simple_models import Base
    # 使用create_all时添加checkfirst=True参数，避免重复创建表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("已初始化数据库表（simple_models）")
except Exception as e:
    print(f"初始化数据库表时出错: {e}")

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

# 模拟LLM配置路由
@app.get("/api/llm-config/providers")
async def get_providers():
    """获取大模型供应商列表（模拟数据）"""
    return [
        {"id": 1, "name": "OpenAI", "description": "OpenAI API", "base_url": "https://api.openai.com/v1", "is_public": True},
        {"id": 2, "name": "Anthropic", "description": "Anthropic Claude API", "base_url": "https://api.anthropic.com", "is_public": True},
        {"id": 3, "name": "Gemini", "description": "Google Gemini API", "base_url": "https://generativelanguage.googleapis.com", "is_public": True},
        {"id": 4, "name": "DeepSeek", "description": "DeepSeek AI API", "base_url": "https://api.deepseek.com", "is_public": True}
    ]

@app.get("/api/llm-config/models")
async def get_models():
    """获取大模型列表（模拟数据）"""
    return [
        {"id": 1, "name": "gpt-4", "provider_id": 1, "api_key": "sk-***********", "is_active": True, "is_public": True, "max_tokens": 8192, "temperature": 0.7},
        {"id": 2, "name": "gpt-3.5-turbo", "provider_id": 1, "api_key": "sk-***********", "is_active": True, "is_public": True, "max_tokens": 4096, "temperature": 0.7},
        {"id": 3, "name": "claude-3-opus", "provider_id": 2, "api_key": "sk_ant-***********", "is_active": True, "is_public": True, "max_tokens": 100000, "temperature": 0.7},
        {"id": 4, "name": "deepseek-chat", "provider_id": 4, "api_key": "sk-***********", "is_active": True, "is_public": True, "max_tokens": 4096, "temperature": 0.7},
        {"id": 5, "name": "deepseek-reasoner", "provider_id": 4, "api_key": "sk-***********", "is_active": True, "is_public": True, "max_tokens": 4096, "temperature": 0.7}
    ]

# 添加LLM模型API
@app.get("/api/llm/models")
async def get_llm_models():
    """获取大模型列表（模拟数据）"""
    return [
        {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
        {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
        {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
        {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
    ]

# 添加LLM请求模型
class LLMRequest(BaseModel):
    content: str
    model_id: Optional[int] = None
    options: Optional[Dict[str, Any]] = None

class DatabaseAnalysisRequest(BaseModel):
    database_id: int
    model_id: Optional[int] = None
    prompt: str

# 添加LLM分析API
@app.post("/api/llm/analyze")
async def analyze_text(request: LLMRequest):
    """使用大模型分析文本（模拟）"""
    return {
        "result": f"## 分析结果\n\n这段文本主要讨论了以下几个方面：\n\n1. 主题：人工智能在现代社会的应用\n2. 观点：人工智能正在改变各个行业的工作方式\n3. 情感：中性，偏向积极\n\n### 关键观点\n\n- 人工智能技术正在快速发展\n- 各行各业都在采用AI解决方案\n- 需要关注AI的伦理问题",
        "type": "analysis"
    }

@app.post("/api/llm/generate")
async def generate_text(request: LLMRequest):
    """使用大模型生成文本（模拟）"""
    return {
        "result": f"# {request.content}\n\n人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n## 主要应用领域\n\n1. **医疗保健** - 疾病诊断、药物研发、个性化治疗\n2. **金融** - 风险评估、欺诈检测、算法交易\n3. **制造业** - 预测性维护、质量控制、供应链优化\n4. **客户服务** - 聊天机器人、个性化推荐、情感分析",
        "type": "generation"
    }

@app.post("/api/llm/summarize")
async def summarize_text(request: LLMRequest):
    """使用大模型生成摘要（模拟）"""
    return {
        "result": f"## 摘要\n\n该文本讨论了人工智能的发展及其对社会的影响。主要观点包括AI技术正在各行业广泛应用，带来效率提升和创新，但也引发了关于隐私、就业和伦理的担忧。作者认为需要平衡技术进步与社会影响，建立适当的监管框架。",
        "type": "summary"
    }

@app.post("/api/llm/extract-keywords")
async def extract_keywords(request: LLMRequest):
    """使用大模型提取关键词（模拟）"""
    return {
        "result": ["人工智能", "机器学习", "自动化", "效率提升", "技术创新", "伦理考量", "隐私保护", "就业影响", "监管框架", "社会变革"],
        "type": "keywords"
    }

@app.post("/api/llm/analyze-database")
async def analyze_database(request: DatabaseAnalysisRequest):
    """使用大模型分析数据库内容（模拟）"""
    return {
        "result": f"## 数据库分析结果\n\n基于数据库ID {request.database_id}的分析：\n\n### 主要发现\n\n1. 销售趋势呈现季节性波动，第四季度表现最佳\n2. 客户满意度与产品质量高度相关\n3. 价格变动对销量的影响因产品类别而异\n\n### 建议\n\n- 增加第四季度的库存和营销预算\n- 重点关注产品质量改进\n- 针对不同产品类别制定差异化定价策略",
        "type": "database_analysis"
    }

@app.get("/api/llm-config/roles")
async def get_roles():
    """获取大模型角色列表（模拟数据）"""
    return [
        {"id": 1, "name": "通用助手", "description": "通用AI助手", "system_prompt": "你是一个有用的AI助手。", "model_id": 1, "is_default": True, "is_public": True},
        {"id": 2, "name": "程序员", "description": "编程助手", "system_prompt": "你是一个专业的程序员，擅长解决编程问题。", "model_id": 1, "is_default": False, "is_public": True},
        {"id": 3, "name": "写作助手", "description": "写作辅助", "system_prompt": "你是一个专业的写作助手，擅长文学创作和文章润色。", "model_id": 2, "is_default": True, "is_public": True},
        {"id": 4, "name": "默认助手", "description": "DeepSeek 默认助手", "system_prompt": "你是由DeepSeek AI开发的智能助手，可以回答用户的各种问题并提供帮助。", "model_id": 4, "is_default": True, "is_public": True},
        {"id": 5, "name": "推理助手", "description": "DeepSeek 推理助手", "system_prompt": "你是由DeepSeek AI开发的推理助手，擅长分析问题并提供详细的推理过程。", "model_id": 5, "is_default": True, "is_public": True}
    ]

@app.put("/api/llm-config/models/{model_id}")
async def update_model(model_id: int, model: dict):
    """更新LLM模型（模拟）"""
    return {"id": model_id, **model}

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
