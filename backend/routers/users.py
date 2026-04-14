from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from db.models import User, File, Share, ChatRecord, Playlist, PlaylistItem, VideoProgress, Notification
from main import get_db
from routers.auth import get_current_active_user

router = APIRouter()

class UserUpdate(BaseModel):
    username: str
    email: str
    nickname: str
    is_admin: bool = False
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以访问用户列表"
        )
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此用户信息"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此用户信息"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否被其他用户使用
    if user_update.username != user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
    
    # 检查邮箱是否被其他用户使用
    if user_update.email != user.email and user_update.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    user.username = user_update.username
    user.email = user_update.email
    user.nickname = user_update.nickname
    if current_user.is_admin:
        user.is_admin = user_update.is_admin
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除用户"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除所有关联的数据
    # 删除通知
    db.query(Notification).filter(Notification.user_id == user_id).delete()
    
    # 删除视频进度
    db.query(VideoProgress).filter(VideoProgress.user_id == user_id).delete()
    
    # 删除歌单项
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).all()
    for playlist in playlists:
        db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist.id).delete()
    
    # 删除歌单
    db.query(Playlist).filter(Playlist.user_id == user_id).delete()
    
    # 删除聊天记录
    db.query(ChatRecord).filter(
        (ChatRecord.sender_id == user_id) | (ChatRecord.receiver_id == user_id)
    ).delete()
    
    # 删除共享
    db.query(Share).filter(
        (Share.creator_id == user_id) | (Share.receiver_id == user_id)
    ).delete()
    
    # 删除文件
    db.query(File).filter(File.user_id == user_id).delete()
    
    # 删除用户
    db.delete(user)
    db.commit()
    return {"message": "用户删除成功"}
