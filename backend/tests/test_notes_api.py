import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_notes_unauthorized(client):
    """测试未授权获取笔记列表"""
    response = client.get("/api/notes/")
    assert response.status_code == 401
    assert "detail" in response.json()

@pytest.mark.skip(reason="需要实际的数据库连接和认证")
def test_create_note(client, test_db):
    """测试创建笔记"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 创建笔记
    response = client.post(
        "/api/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note."
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note."
    assert "id" in data

@pytest.mark.skip(reason="需要实际的数据库连接和认证")
def test_get_notes(client, test_db):
    """测试获取笔记列表"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 获取笔记列表
    response = client.get(
        "/api/notes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.skip(reason="需要实际的数据库连接和认证")
def test_update_note(client, test_db):
    """测试更新笔记"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 创建笔记
    create_response = client.post(
        "/api/notes/",
        json={
            "title": "Original Title",
            "content": "Original Content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]
    
    # 更新笔记
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "Updated Title",
            "content": "Updated Content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == note_id

@pytest.mark.skip(reason="需要实际的数据库连接和认证")
def test_delete_note(client, test_db):
    """测试删除笔记"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 创建笔记
    create_response = client.post(
        "/api/notes/",
        json={
            "title": "Note to Delete",
            "content": "This note will be deleted."
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]
    
    # 删除笔记
    delete_response = client.delete(
        f"/api/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204
    
    # 确认笔记已删除
    get_response = client.get(
        f"/api/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404
