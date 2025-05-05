from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import os

# 检测环境
IS_DOCKER = os.environ.get("IS_DOCKER", "false").lower() == "true"

from core.dependencies import get_db, get_current_user
from models.schemas import ConversationCreate, ConversationResponse, MessageResponse, UserResponse
from core.services import conversation_service

router = APIRouter()

# 如果是Docker环境，使用简化实现的模拟数据
if IS_DOCKER:
    # 模拟数据
    conversations = [
        {"id": 1, "note_id": 1, "role_id": 1, "created_at": "2023-05-10T10:00:00Z", "updated_at": "2023-05-10T10:02:00Z"},
        {"id": 2, "note_id": 1, "role_id": 3, "created_at": "2023-05-11T14:00:00Z", "updated_at": "2023-05-11T14:02:00Z"}
    ]

    messages = {
        1: [
            {"id": 1, "conversation_id": 1, "content": "你好，我是通用助手，有什么可以帮助你的？", "role": "assistant", "created_at": "2023-05-10T10:00:00Z"},
            {"id": 2, "conversation_id": 1, "content": "我想了解一下人工智能的基础知识", "role": "user", "created_at": "2023-05-10T10:01:00Z"},
            {"id": 3, "conversation_id": 1, "content": "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n主要的AI领域包括：\n\n1. **机器学习** - 使计算机能够从数据中学习，而无需明确编程\n2. **深度学习** - 使用神经网络进行复杂模式识别\n3. **自然语言处理** - 使计算机能够理解和生成人类语言\n4. **计算机视觉** - 使计算机能够解释和理解视觉信息\n\n人工智能已经在许多领域找到了应用，包括医疗保健、金融、制造业和客户服务等。", "role": "assistant", "created_at": "2023-05-10T10:02:00Z"}
        ],
        2: [
            {"id": 4, "conversation_id": 2, "content": "你好，我是写作助手，有什么可以帮助你的？", "role": "assistant", "created_at": "2023-05-11T14:00:00Z"},
            {"id": 5, "conversation_id": 2, "content": "我需要写一篇关于环保的文章，有什么建议？", "role": "user", "created_at": "2023-05-11T14:01:00Z"},
            {"id": 6, "conversation_id": 2, "content": "为了写一篇关于环保的文章，我建议以下结构和内容：\n\n## 标题\n**\"保护地球，从我做起：日常生活中的环保实践\"**\n\n## 引言\n- 简述当前环境面临的挑战\n- 强调个人行动的重要性\n- 提出文章的主要目的：分享实用的环保方法\n\n## 主体部分\n\n### 1. 减少塑料使用\n- 使用可重复使用的购物袋\n- 避免一次性塑料制品\n- 选择无塑料包装的产品\n\n### 2. 节约能源\n- 使用节能灯具和电器\n- 合理设置空调温度\n- 不用时关闭电器电源\n\n### 3. 水资源保护\n- 修复漏水的水龙头\n- 收集雨水用于浇花\n- 减少洗澡时间\n\n### 4. 垃圾分类与回收\n- 学习正确的垃圾分类方法\n- 将可回收物品送去回收\n- 尝试堆肥厨余垃圾\n\n### 5. 绿色出行\n- 使用公共交通工具\n- 骑自行车或步行\n- 考虑拼车或电动汽车\n\n## 结论\n- 总结环保行动的集体影响\n- 鼓励读者从小事做起\n- 展望更可持续的未来\n\n希望这个框架对你有所帮助！", "role": "assistant", "created_at": "2023-05-11T14:02:00Z"}
        ]
    }

# Docker环境下的简化路由
if IS_DOCKER:
    @router.get("/note/{note_id}", response_model=List[Dict[str, Any]])
    async def get_note_conversations(note_id: int):
        """获取笔记的对话列表"""
        return [c for c in conversations if c["note_id"] == note_id]

    @router.get("/{conversation_id}/messages", response_model=List[Dict[str, Any]])
    async def get_conversation_messages(conversation_id: int):
        """获取对话的消息列表"""
        return messages.get(conversation_id, [])

    @router.post("/", response_model=Dict[str, Any])
    async def create_conversation(note_id: int, role_id: int):
        """创建新对话"""
        conversation_id = max([c["id"] for c in conversations]) + 1 if conversations else 1
        new_conversation = {
            "id": conversation_id,
            "note_id": note_id,
            "role_id": role_id,
            "created_at": "2023-05-12T10:00:00Z",
            "updated_at": "2023-05-12T10:00:00Z"
        }
        conversations.append(new_conversation)

        # 创建初始消息
        messages[conversation_id] = [
            {
                "id": 1,
                "conversation_id": conversation_id,
                "content": "你好，我是AI助手，有什么可以帮助你的？",
                "role": "assistant",
                "created_at": "2023-05-12T10:00:00Z"
            }
        ]

        return new_conversation

    @router.post("/{conversation_id}/messages", response_model=Dict[str, Any])
    async def create_message(conversation_id: int, content: str, role: str):
        """创建新消息"""
        if conversation_id not in [c["id"] for c in conversations]:
            raise HTTPException(status_code=404, detail="对话不存在")

        conversation_messages = messages.get(conversation_id, [])
        message_id = max([m["id"] for m in conversation_messages]) + 1 if conversation_messages else 1

        new_message = {
            "id": message_id,
            "conversation_id": conversation_id,
            "content": content,
            "role": role,
            "created_at": "2023-05-12T10:01:00Z"
        }

        if conversation_id not in messages:
            messages[conversation_id] = []

        messages[conversation_id].append(new_message)

        # 如果是用户消息，自动添加AI回复
        if role == "user":
            ai_message_id = message_id + 1
            ai_message = {
                "id": ai_message_id,
                "conversation_id": conversation_id,
                "content": f"这是对\"{content}\"的回复。在实际应用中，这里会调用大模型API获取响应。",
                "role": "assistant",
                "created_at": "2023-05-12T10:02:00Z"
            }
            messages[conversation_id].append(ai_message)
            return ai_message

        return new_message

    @router.delete("/{conversation_id}", response_model=Dict[str, str])
    async def delete_conversation(conversation_id: int):
        """删除对话"""
        for i, c in enumerate(conversations):
            if c["id"] == conversation_id:
                del conversations[i]
                if conversation_id in messages:
                    del messages[conversation_id]
                return {"message": "对话已删除"}

        raise HTTPException(status_code=404, detail="对话不存在")

# 非Docker环境下的完整路由
else:
    @router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
    async def create_conversation(
        conversation: ConversationCreate,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """创建新的对话"""
        # 确保对话关联到当前用户
        conversation.user_id = current_user.id
        return conversation_service.create_conversation(db=db, conversation=conversation)

    @router.get("/note/{note_id}", response_model=List[ConversationResponse])
    async def get_note_conversations(
        note_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """获取笔记的对话列表"""
        return conversation_service.get_conversations(
            db=db,
            note_id=note_id,
            skip=skip,
            limit=limit,
            user_id=current_user.id
        )

    @router.get("/{conversation_id}", response_model=ConversationResponse)
    async def get_conversation(
        conversation_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """获取单个对话详情"""
        db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
        if db_conversation is None:
            raise HTTPException(status_code=404, detail="对话不存在")

        # 检查对话是否属于当前用户
        if db_conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="没有权限访问此对话")

        return db_conversation

    @router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_conversation(
        conversation_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """删除对话"""
        db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
        if db_conversation is None:
            raise HTTPException(status_code=404, detail="对话不存在")

        # 检查对话是否属于当前用户
        if db_conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="没有权限删除此对话")

        conversation_service.delete_conversation(db=db, conversation_id=conversation_id)
        return {"detail": "对话已删除"}

    @router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
    async def get_conversation_messages(
        conversation_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """获取对话的消息列表"""
        db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
        if db_conversation is None:
            raise HTTPException(status_code=404, detail="对话不存在")

        # 检查对话是否属于当前用户
        if db_conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="没有权限访问此对话")

        return conversation_service.get_messages(
            db=db,
            conversation_id=conversation_id,
            skip=skip,
            limit=limit
        )

    @router.post("/{conversation_id}/messages", response_model=dict)
    async def send_message(
        conversation_id: int,
        message: str,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """发送消息并获取AI响应"""
        db_conversation = conversation_service.get_conversation(db=db, conversation_id=conversation_id)
        if db_conversation is None:
            raise HTTPException(status_code=404, detail="对话不存在")

        # 检查对话是否属于当前用户
        if db_conversation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="没有权限访问此对话")

        try:
            result = await conversation_service.send_message_and_get_response(
                db=db,
                conversation_id=conversation_id,
                user_message=message
            )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"发送消息失败: {str(e)}"
            )
