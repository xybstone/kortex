# 服务模块初始化文件
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

from core.config import settings
from models.domain import User, Note, Database

# 创建模拟服务
class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        hashed_password = self.get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name", ""),
            is_active=True,
            is_admin=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(db, email=email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

class NoteService:
    def create_note(self, db: Session, note_data: Dict[str, Any]) -> Note:
        db_note = Note(
            title=note_data["title"],
            content=note_data["content"],
            user_id=note_data["user_id"]
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    def get_notes(self, db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None, user_id: Optional[int] = None) -> List[Note]:
        query = db.query(Note)
        if user_id:
            query = query.filter(Note.user_id == user_id)
        if search:
            query = query.filter(Note.title.contains(search) | Note.content.contains(search))
        return query.offset(skip).limit(limit).all()

    def get_note(self, db: Session, note_id: int) -> Optional[Note]:
        return db.query(Note).filter(Note.id == note_id).first()

    def update_note(self, db: Session, note_id: int, note_data: Dict[str, Any]) -> Optional[Note]:
        db_note = self.get_note(db, note_id=note_id)
        if db_note:
            for key, value in note_data.items():
                setattr(db_note, key, value)
            db.commit()
            db.refresh(db_note)
        return db_note

    def delete_note(self, db: Session, note_id: int) -> bool:
        db_note = self.get_note(db, note_id=note_id)
        if db_note:
            db.delete(db_note)
            db.commit()
            return True
        return False

class LLMService:
    async def analyze_text(self, db: Session, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "result": f"分析结果：{request['content']}",
            "type": "analysis"
        }

    async def generate_text(self, db: Session, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "result": f"生成结果：{request['content']}",
            "type": "generation"
        }

    async def summarize_text(self, db: Session, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "result": f"摘要结果：{request['content']}",
            "type": "summary"
        }

    async def extract_keywords(self, db: Session, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "result": ["关键词1", "关键词2", "关键词3"],
            "type": "keywords"
        }

    async def analyze_database(self, db: Session, database_id: int, prompt: str, model_id: Optional[int] = None) -> Dict[str, Any]:
        return {
            "result": f"数据库分析结果：{prompt}",
            "type": "database_analysis"
        }

    async def get_available_models(self, db: Session) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "gpt-4", "provider": "OpenAI", "is_active": True},
            {"id": 2, "name": "gpt-3.5-turbo", "provider": "OpenAI", "is_active": True},
            {"id": 3, "name": "claude-3-opus", "provider": "Anthropic", "is_active": True},
            {"id": 4, "name": "deepseek-chat", "provider": "DeepSeek", "is_active": True}
        ]

class DatabaseService:
    def create_database(self, db: Session, database: Dict[str, Any]) -> Database:
        """创建新数据库"""
        db_database = Database(
            name=database["name"],
            description=database["description"],
            user_id=database["user_id"]
        )
        db.add(db_database)
        db.commit()
        db.refresh(db_database)
        return db_database

    def get_databases(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[Database]:
        """获取数据库列表"""
        query = db.query(Database)

        # 如果提供了用户ID，只返回该用户的数据库
        if user_id:
            query = query.filter(Database.user_id == user_id)

        # 如果提供了搜索关键词，在名称和描述中搜索
        if search:
            query = query.filter(
                (Database.name.ilike(f"%{search}%")) |
                (Database.description.ilike(f"%{search}%"))
            )

        # 获取分页结果
        return query.order_by(Database.name).offset(skip).limit(limit).all()

    def get_database(self, db: Session, database_id: int) -> Optional[Database]:
        """获取单个数据库详情"""
        return db.query(Database).filter(Database.id == database_id).first()

    def update_database(self, db: Session, database_id: int, database: Dict[str, Any]) -> Optional[Database]:
        """更新数据库"""
        db_database = self.get_database(db, database_id=database_id)
        if db_database:
            for key, value in database.items():
                if hasattr(db_database, key):
                    setattr(db_database, key, value)
            db.commit()
            db.refresh(db_database)
        return db_database

    def delete_database(self, db: Session, database_id: int) -> bool:
        """删除数据库"""
        db_database = self.get_database(db, database_id=database_id)
        if db_database:
            db.delete(db_database)
            db.commit()
            return True
        return False

    def get_database_tables(self, db: Session, database_id: int) -> List[Dict[str, Any]]:
        """获取数据库中的表格列表（模拟）"""
        return [
            {"id": 1, "name": "表格1", "database_id": database_id},
            {"id": 2, "name": "表格2", "database_id": database_id},
            {"id": 3, "name": "表格3", "database_id": database_id}
        ]

    async def import_database(
        self,
        db: Session,
        name: str,
        description: Optional[str],
        file: Any,
        user_id: int
    ) -> Database:
        """导入数据库文件（模拟）"""
        # 创建数据库记录
        db_database = Database(
            name=name,
            description=description,
            user_id=user_id
        )
        db.add(db_database)
        db.commit()
        db.refresh(db_database)
        return db_database

    def get_table_data(
        self,
        db: Session,
        database_id: int,
        table_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取表格数据（模拟）"""
        return {
            "columns": ["id", "name", "value"],
            "rows": [
                {"id": 1, "name": "测试1", "value": 100},
                {"id": 2, "name": "测试2", "value": 200},
                {"id": 3, "name": "测试3", "value": 300}
            ],
            "total": 3
        }

class LLMConfigService:
    def create_provider(self, db: Session, provider: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的LLM供应商（模拟）"""
        return {
            "id": 1,
            "name": provider["name"],
            "api_base": provider["api_base"],
            "api_key": provider["api_key"],
            "is_active": True,
            "user_id": provider["user_id"],
            "created_at": datetime.now()
        }

    def get_providers(self, db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取LLM供应商列表（模拟）"""
        return [
            {
                "id": 1,
                "name": "OpenAI",
                "api_base": "https://api.openai.com/v1",
                "api_key": "sk-***",
                "is_active": True,
                "user_id": 1,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "name": "Anthropic",
                "api_base": "https://api.anthropic.com",
                "api_key": "sk-***",
                "is_active": True,
                "user_id": 1,
                "created_at": datetime.now()
            }
        ]

    def get_provider(self, db: Session, provider_id: int) -> Optional[Dict[str, Any]]:
        """获取单个LLM供应商详情（模拟）"""
        providers = self.get_providers(db)
        for provider in providers:
            if provider["id"] == provider_id:
                return provider
        return None

    def update_provider(self, db: Session, provider_id: int, provider: Dict[str, Any]) -> Dict[str, Any]:
        """更新LLM供应商（模拟）"""
        db_provider = self.get_provider(db, provider_id)
        if db_provider:
            for key, value in provider.items():
                if key in db_provider:
                    db_provider[key] = value
        return db_provider

    def delete_provider(self, db: Session, provider_id: int) -> bool:
        """删除LLM供应商（模拟）"""
        return True

    def create_model(self, db: Session, model: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的LLM模型（模拟）"""
        return {
            "id": 1,
            "name": model["name"],
            "provider_id": model["provider_id"],
            "model_id": model["model_id"],
            "is_active": True,
            "user_id": model["user_id"],
            "created_at": datetime.now()
        }

    def get_models(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        provider_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取LLM模型列表（模拟）"""
        return [
            {
                "id": 1,
                "name": "GPT-4",
                "provider_id": 1,
                "model_id": "gpt-4",
                "is_active": True,
                "user_id": 1,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "name": "GPT-3.5 Turbo",
                "provider_id": 1,
                "model_id": "gpt-3.5-turbo",
                "is_active": True,
                "user_id": 1,
                "created_at": datetime.now()
            }
        ]

    def get_model(self, db: Session, model_id: int) -> Optional[Dict[str, Any]]:
        """获取单个LLM模型详情（模拟）"""
        models = self.get_models(db)
        for model in models:
            if model["id"] == model_id:
                return model
        return None

    def update_model(self, db: Session, model_id: int, model: Dict[str, Any]) -> Dict[str, Any]:
        """更新LLM模型（模拟）"""
        db_model = self.get_model(db, model_id)
        if db_model:
            for key, value in model.items():
                if key in db_model:
                    db_model[key] = value
        return db_model

    def delete_model(self, db: Session, model_id: int) -> bool:
        """删除LLM模型（模拟）"""
        return True

    def create_role(self, db: Session, role: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的LLM角色（模拟）"""
        return {
            "id": 1,
            "name": role["name"],
            "description": role["description"],
            "system_prompt": role["system_prompt"],
            "model_id": role["model_id"],
            "is_default": role.get("is_default", False),
            "user_id": role["user_id"],
            "created_at": datetime.now()
        }

    def get_roles(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        model_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取LLM角色列表（模拟）"""
        return [
            {
                "id": 1,
                "name": "助手",
                "description": "通用助手角色",
                "system_prompt": "你是一个有用的AI助手",
                "model_id": 1,
                "is_default": True,
                "user_id": 1,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "name": "程序员",
                "description": "编程助手角色",
                "system_prompt": "你是一个专业的编程助手",
                "model_id": 1,
                "is_default": False,
                "user_id": 1,
                "created_at": datetime.now()
            }
        ]

    def get_role(self, db: Session, role_id: int) -> Optional[Dict[str, Any]]:
        """获取单个LLM角色详情（模拟）"""
        roles = self.get_roles(db)
        for role in roles:
            if role["id"] == role_id:
                return role
        return None

    def update_role(self, db: Session, role_id: int, role: Dict[str, Any]) -> Dict[str, Any]:
        """更新LLM角色（模拟）"""
        db_role = self.get_role(db, role_id)
        if db_role:
            for key, value in role.items():
                if key in db_role:
                    db_role[key] = value
        return db_role

    def delete_role(self, db: Session, role_id: int) -> bool:
        """删除LLM角色（模拟）"""
        return True

    def get_default_role(self, db: Session, model_id: int) -> Optional[Dict[str, Any]]:
        """获取模型的默认角色（模拟）"""
        roles = self.get_roles(db)
        for role in roles:
            if role["model_id"] == model_id and role["is_default"]:
                return role
        return None

class ConversationService:
    def create_conversation(self, db: Session, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的对话（模拟）"""
        return {
            "id": 1,
            "note_id": conversation["note_id"],
            "role_id": conversation["role_id"],
            "user_id": conversation["user_id"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": []
        }

    def get_conversations(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        note_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取对话列表（模拟）"""
        return [
            {
                "id": 1,
                "note_id": 1,
                "role_id": 1,
                "user_id": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "messages": []
            },
            {
                "id": 2,
                "note_id": 1,
                "role_id": 2,
                "user_id": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "messages": []
            }
        ]

    def get_conversation(self, db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
        """获取单个对话详情（模拟）"""
        conversations = self.get_conversations(db)
        for conversation in conversations:
            if conversation["id"] == conversation_id:
                return conversation
        return None

    def delete_conversation(self, db: Session, conversation_id: int) -> bool:
        """删除对话（模拟）"""
        return True

    def add_message(self, db: Session, message: Dict[str, Any]) -> Dict[str, Any]:
        """添加消息（模拟）"""
        return {
            "id": 1,
            "content": message["content"],
            "role": message["role"],
            "conversation_id": message["conversation_id"],
            "created_at": datetime.now()
        }

    def get_messages(self, db: Session, conversation_id: int) -> List[Dict[str, Any]]:
        """获取对话消息列表（模拟）"""
        return [
            {
                "id": 1,
                "content": "你好，有什么可以帮助你的？",
                "role": "assistant",
                "conversation_id": conversation_id,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "content": "我想了解一下Python的基础语法",
                "role": "user",
                "conversation_id": conversation_id,
                "created_at": datetime.now()
            }
        ]

# 创建服务实例
auth_service = AuthService()
note_service = NoteService()
llm_service = LLMService()
database_service = DatabaseService()
llm_config_service = LLMConfigService()
conversation_service = ConversationService()
