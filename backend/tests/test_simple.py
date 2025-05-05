from fastapi.testclient import TestClient
from main_test import app

def test_simple():
    """最简单的测试"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "欢迎使用Kortex API"}
