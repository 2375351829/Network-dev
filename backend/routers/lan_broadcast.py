from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import socket
import threading
import json
from db.models import User
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# 配置
BROADCAST_PORT = 50007
BROADCAST_INTERVAL = 5  # 秒

# 全局变量
broadcast_thread = None
broadcast_running = False
received_messages = []

# Pydantic模型
class BroadcastMessage(BaseModel):
    message: str
    type: str = "info"  # info, warning, error, system
    sender: str = "LanFileHub"

class BroadcastStatus(BaseModel):
    running: bool
    last_broadcast: Optional[datetime] = None
    received_messages: List[dict]

# 工具函数
def broadcast_message(message: str, message_type: str = "info"):
    """发送广播消息"""
    try:
        # 创建UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # 准备消息数据
        message_data = {
            "message": message,
            "type": message_type,
            "sender": "LanFileHub",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 发送广播
        sock.sendto(json.dumps(message_data).encode(), ("<broadcast>", BROADCAST_PORT))
        sock.close()
        
        return True
    except Exception as e:
        print(f"Broadcast failed: {e}")
        return False

def receive_broadcasts():
    """接收广播消息"""
    global received_messages
    
    try:
        # 创建UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", BROADCAST_PORT))
        
        while broadcast_running:
            # 接收消息
            data, addr = sock.recvfrom(1024)
            try:
                message = json.loads(data.decode())
                # 添加到接收消息列表
                received_messages.append({
                    "message": message.get("message"),
                    "type": message.get("type"),
                    "sender": message.get("sender"),
                    "timestamp": message.get("timestamp"),
                    "from": addr[0]
                })
                # 限制消息数量
                if len(received_messages) > 100:
                    received_messages = received_messages[-100:]
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"Receive broadcast failed: {e}")

# 路由
@router.post("/send")
async def send_broadcast(
    broadcast: BroadcastMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """发送广播消息"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = broadcast_message(broadcast.message, broadcast.type)
    if success:
        return {"message": "Broadcast sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send broadcast")

@router.get("/status")
async def get_broadcast_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取广播状态"""
    global broadcast_running, received_messages
    
    return BroadcastStatus(
        running=broadcast_running,
        received_messages=received_messages
    )

@router.post("/start")
async def start_broadcast_service(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """启动广播服务"""
    global broadcast_running, broadcast_thread
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not broadcast_running:
        broadcast_running = True
        # 启动接收线程
        broadcast_thread = threading.Thread(target=receive_broadcasts, daemon=True)
        broadcast_thread.start()
        
        return {"message": "Broadcast service started"}
    else:
        return {"message": "Broadcast service is already running"}

@router.post("/stop")
async def stop_broadcast_service(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """停止广播服务"""
    global broadcast_running, broadcast_thread
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if broadcast_running:
        broadcast_running = False
        if broadcast_thread:
            broadcast_thread.join(timeout=1)
        
        return {"message": "Broadcast service stopped"}
    else:
        return {"message": "Broadcast service is not running"}

@router.get("/messages")
async def get_received_messages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取接收到的广播消息"""
    global received_messages
    return received_messages

@router.post("/messages/clear")
async def clear_received_messages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """清空接收到的广播消息"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    global received_messages
    received_messages = []
    
    return {"message": "Received messages cleared"}

# 初始化广播服务
def init_broadcast_service():
    """初始化广播服务"""
    global broadcast_running, broadcast_thread
    
    broadcast_running = True
    # 启动接收线程
    broadcast_thread = threading.Thread(target=receive_broadcasts, daemon=True)
    broadcast_thread.start()

# 初始化广播服务
init_broadcast_service()