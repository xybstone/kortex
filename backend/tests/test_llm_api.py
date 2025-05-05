import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_llm_status(client):
    """测试LLM状态端点"""
    response = client.get("/api/llm/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "可用"

@pytest.mark.skip(reason="需要实际的LLM API")
def test_analyze_text(client):
    """测试文本分析功能"""
    response = client.post(
        "/api/llm/analyze",
        json={
            "content": "人工智能正在改变我们的生活方式。",
            "model_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "type" in data
    assert data["type"] == "analysis"

@pytest.mark.skip(reason="需要实际的LLM API")
def test_generate_text(client):
    """测试文本生成功能"""
    response = client.post(
        "/api/llm/generate",
        json={
            "content": "写一篇关于人工智能的短文",
            "model_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "type" in data
    assert data["type"] == "generation"

@pytest.mark.skip(reason="需要实际的LLM API")
def test_summarize_text(client):
    """测试文本摘要功能"""
    response = client.post(
        "/api/llm/summarize",
        json={
            "content": "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。主要的AI领域包括机器学习、深度学习、自然语言处理和计算机视觉。人工智能已经在许多领域找到了应用，包括医疗保健、金融、制造业和客户服务等。",
            "model_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "type" in data
    assert data["type"] == "summary"

@pytest.mark.skip(reason="需要实际的LLM API")
def test_extract_keywords(client):
    """测试关键词提取功能"""
    response = client.post(
        "/api/llm/extract-keywords",
        json={
            "content": "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。",
            "model_id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "type" in data
    assert data["type"] == "keywords"
    assert isinstance(data["result"], list)

def test_get_models(client):
    """测试获取模型列表"""
    response = client.get("/api/llm/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    assert "provider" in data[0]
    assert "is_active" in data[0]
