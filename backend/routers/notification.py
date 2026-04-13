from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from db.models import User, Notification
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# Pydantic模型
class NotificationBase(BaseModel):
    title: str
    content: str
    notification_type: str = "system"  # system, file, share, chat, backup
    related_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    user_id: Optional[int] = None  # 为None时表示系统级通知

class NotificationResponse(NotificationBase):
    id: int
    user_id: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationUpdate(BaseModel):
    is_read: bool

# 路由
@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建通知"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_notification = Notification(
        title=notification.title,
        content=notification.content,
        notification_type=notification.notification_type,
        user_id=notification.user_id,
        related_id=notification.related_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return db_notification

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的通知"""
    # 获取用户的通知和系统级通知
    notifications = db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
    
    return notifications

@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取未读通知"""
    notifications = db.query(Notification).filter(
        ((Notification.user_id == current_user.id) | (Notification.user_id == None)),
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).all()
    
    return notifications

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新通知状态"""
    # 获取通知
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # 检查权限（只能更新自己的通知或系统通知）
    if notification.user_id is not None and notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 更新状态
    notification.is_read = notification_update.is_read
    db.commit()
    db.refresh(notification)
    
    return notification

@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """标记所有通知为已读"""
    # 更新用户的通知和系统通知
    db.query(Notification).filter(
        ((Notification.user_id == current_user.id) | (Notification.user_id == None)),
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除通知"""
    # 获取通知
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # 检查权限（只能删除自己的通知或系统通知）
    if notification.user_id is not None and notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 删除通知
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted successfully"}

@router.delete("/delete-all")
async def delete_all_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除所有通知"""
    # 删除用户的通知
    db.query(Notification).filter(Notification.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "All notifications deleted successfully"}