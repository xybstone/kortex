from fastapi import FastAPI
from fastapi.testclient import TestClient

# 创建一个简单的应用
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def test_direct():
    """直接测试，不依赖于conftest.py"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
