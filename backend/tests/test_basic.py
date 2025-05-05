from fastapi.testclient import TestClient
import pytest

def test_root(client):
    """测试根路由"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "欢迎使用Kortex API"}

def test_health(client):
    """测试健康检查端点"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.skip(reason="需要实际的数据库连接")
def test_register_user(client):
    """测试用户注册"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
