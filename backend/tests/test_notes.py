from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.db_models import User, Note
from core.security import get_password_hash

def test_create_note(client: TestClient, test_db: Session):
    """测试创建笔记"""
    # 创建用户
    hashed_password = get_password_hash("password123")
    user = User(
        email="note@example.com",
        hashed_password=hashed_password,
        full_name="Note User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "note@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

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

def test_get_notes(client: TestClient, test_db: Session):
    """测试获取笔记列表"""
    # 创建用户
    hashed_password = get_password_hash("password123")
    user = User(
        email="notes@example.com",
        hashed_password=hashed_password,
        full_name="Notes User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # 创建笔记
    note1 = Note(
        title="Note 1",
        content="Content 1",
        user_id=user.id
    )
    note2 = Note(
        title="Note 2",
        content="Content 2",
        user_id=user.id
    )
    test_db.add(note1)
    test_db.add(note2)
    test_db.commit()

    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "notes@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # 获取笔记列表
    response = client.get(
        "/api/notes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] in ["Note 1", "Note 2"]
    assert data[1]["title"] in ["Note 1", "Note 2"]

def test_get_note(client: TestClient, test_db: Session):
    """测试获取单个笔记"""
    # 创建用户
    hashed_password = get_password_hash("password123")
    user = User(
        email="getnote@example.com",
        hashed_password=hashed_password,
        full_name="Get Note User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # 创建笔记
    note = Note(
        title="Get Note",
        content="Get Note Content",
        user_id=user.id
    )
    test_db.add(note)
    test_db.commit()

    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "getnote@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # 获取笔记
    response = client.get(
        f"/api/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Note"
    assert data["content"] == "Get Note Content"
    assert data["id"] == note.id

def test_update_note(client: TestClient, test_db: Session):
    """测试更新笔记"""
    # 创建用户
    hashed_password = get_password_hash("password123")
    user = User(
        email="updatenote@example.com",
        hashed_password=hashed_password,
        full_name="Update Note User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # 创建笔记
    note = Note(
        title="Original Title",
        content="Original Content",
        user_id=user.id
    )
    test_db.add(note)
    test_db.commit()

    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "updatenote@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # 更新笔记
    response = client.put(
        f"/api/notes/{note.id}",
        json={
            "title": "Updated Title",
            "content": "Updated Content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == note.id

def test_delete_note(client: TestClient, test_db: Session):
    """测试删除笔记"""
    # 创建用户
    hashed_password = get_password_hash("password123")
    user = User(
        email="deletenote@example.com",
        hashed_password=hashed_password,
        full_name="Delete Note User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # 创建笔记
    note = Note(
        title="Delete Note",
        content="Delete Note Content",
        user_id=user.id
    )
    test_db.add(note)
    test_db.commit()

    # 登录
    response = client.post(
        "/api/auth/login",
        data={
            "username": "deletenote@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # 删除笔记
    response = client.delete(
        f"/api/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # 确认笔记已删除
    response = client.get(
        f"/api/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
