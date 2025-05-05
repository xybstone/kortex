import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main_test import app
from api.dependencies.database import get_db
from models.domain import BaseModel

# 创建内存数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
BaseModel.metadata.create_all(bind=engine)

@pytest.fixture
def test_db():
    """测试数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # 使用测试数据库会话
    yield session

    # 清理
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(test_db):
    """测试客户端"""
    # 覆盖依赖项
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # 创建测试客户端
    with TestClient(app) as client:
        yield client

    # 清理
    app.dependency_overrides.clear()
