from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json
from typing import Dict, List, Optional
from db.models import User, ChatRecord
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# 存储活跃的WebSocket连接
active_connections: Dict[int, WebSocket] = {}

# Pydantic模型
class MessageBase(BaseModel):
    receiver_id: int
    message: str
    message_type: str = "text"
    file_id: Optional[int] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    read_status: bool
    created_at: datetime

    class Config:
        orm_mode = True

class WebSocketMessage(BaseModel):
    type: str
    data: dict

# 工具函数
async def broadcast_message(message: dict):
    """广播消息给所有在线用户"""
    for connection in active_connections.values():
        await connection.send_json(message)

async def send_personal_message(user_id: int, message: dict):
    """发送个人消息"""
    if user_id in active_connections:
        await active_connections[user_id].send_json(message)

# WebSocket端点
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    # 接受连接
    await websocket.accept()
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1000, reason="User not found")
        return
    
    # 存储连接
    active_connections[user_id] = websocket
    
    # 广播用户上线消息
    await broadcast_message({
        "type": "user_online",
        "data": {
            "user_id": user_id,
            "username": user.username,
            "nickname": user.nickname,
            "online": True
        }
    })
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "send_message":
                # 处理发送消息
                receiver_id = message_data["data"].get("receiver_id")
                message_content = message_data["data"].get("message")
                message_type = message_data["data"].get("message_type", "text")
                file_id = message_data["data"].get("file_id")
                
                # 验证接收者
                receiver = db.query(User).filter(User.id == receiver_id).first()
                if not receiver:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Receiver not found"}
                    })
                    continue
                
                # 保存消息到数据库
                chat_record = ChatRecord(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    message=message_content,
                    message_type=message_type,
                    file_id=file_id
                )
                db.add(chat_record)
                db.commit()
                db.refresh(chat_record)
                
                # 发送消息给接收者
                await send_personal_message(receiver_id, {
                    "type": "new_message",
                    "data": {
                        "id": chat_record.id,
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "message": message_content,
                        "message_type": message_type,
                        "file_id": file_id,
                        "read_status": False,
                        "created_at": chat_record.created_at.isoformat()
                    }
                })
                
                # 确认消息发送成功
                await websocket.send_json({
                    "type": "message_sent",
                    "data": {
                        "id": chat_record.id,
                        "status": "success"
                    }
                })
            
            elif message_data.get("type") == "mark_read":
                # 处理消息已读
                message_id = message_data["data"].get("message_id")
                chat_record = db.query(ChatRecord).filter(ChatRecord.id == message_id).first()
                if chat_record and chat_record.receiver_id == user_id:
                    chat_record.read_status = True
                    db.commit()
                    await websocket.send_json({
                        "type": "message_read",
                        "data": {"message_id": message_id}
                    })
    
    except WebSocketDisconnect:
        # 移除连接
        if user_id in active_connections:
            del active_connections[user_id]
        
        # 广播用户下线消息
        await broadcast_message({
            "type": "user_offline",
            "data": {
                "user_id": user_id,
                "username": user.username,
                "nickname": user.nickname,
                "online": False
            }
        })

# HTTP路由
@router.get("/messages/{user_id}", response_model=list[MessageResponse])
async def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取两个用户之间的消息
    messages = db.query(ChatRecord).filter(
        ((ChatRecord.sender_id == current_user.id) & (ChatRecord.receiver_id == user_id)) |
        ((ChatRecord.sender_id == user_id) & (ChatRecord.receiver_id == current_user.id))
    ).order_by(ChatRecord.created_at).all()
    
    return messages

@router.get("/contacts")
async def get_contacts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取用户的联系人列表
    # 这里简化处理，返回所有用户
    users = db.query(User).filter(User.id != current_user.id).all()
    
    contacts = []
    for user in users:
        contacts.append({
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "online": user.id in active_connections
        })
    
    return contacts

@router.get("/online-users")
async def get_online_users():
    # 获取在线用户列表
    online_user_ids = list(active_connections.keys())
    return {"online_user_ids": online_user_ids}