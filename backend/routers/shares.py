from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import os
import secrets
from db.models import User, File, Share
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# Pydantic模型
class ShareBase(BaseModel):
    file_id: int
    receiver_id: Optional[int] = None
    is_public: bool = False
    expires_at: Optional[datetime] = None

class ShareCreate(ShareBase):
    pass

class ShareResponse(ShareBase):
    id: int
    creator_id: int
    share_code: str
    created_at: datetime

    class Config:
        orm_mode = True

# 工具函数
def generate_share_code() -> str:
    return secrets.token_urlsafe(16)

# 路由
@router.post("/create", response_model=ShareResponse)
async def create_share(
    share: ShareCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 检查文件是否存在
    file = db.query(File).filter(File.id == share.file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    if not (file.user_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 生成共享码
    share_code = generate_share_code()
    
    # 创建共享记录
    db_share = Share(
        file_id=share.file_id,
        creator_id=current_user.id,
        receiver_id=share.receiver_id,
        share_code=share_code,
        is_public=share.is_public,
        expires_at=share.expires_at
    )
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    
    return db_share

@router.get("/list", response_model=list[ShareResponse])
async def list_shares(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取用户创建的共享
    shares = db.query(Share).filter(Share.creator_id == current_user.id).all()
    
    # 获取用户接收的共享
    received_shares = db.query(Share).filter(Share.receiver_id == current_user.id).all()
    shares.extend(received_shares)
    
    # 如果是管理员，还可以看到所有公开共享
    if current_user.is_admin:
        public_shares = db.query(Share).filter(Share.is_public == True).all()
        shares.extend(public_shares)
    
    return shares

@router.get("/by-code/{share_code}")
async def get_share_by_code(
    share_code: str,
    db: Session = Depends(get_db)
):
    # 获取共享记录
    share = db.query(Share).filter(Share.share_code == share_code).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # 检查是否过期
    if share.expires_at and share.expires_at < datetime.utcnow():
        raise HTTPException(status_code=404, detail="Share has expired")
    
    # 获取文件
    file = share.file
    if not file or file.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查文件是否存在
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type="application/octet-stream"
    )

@router.delete("/{share_id}")
async def delete_share(
    share_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取共享记录
    share = db.query(Share).filter(Share.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # 检查权限
    if not (share.creator_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 删除共享记录
    db.delete(share)
    db.commit()
    
    return {"message": "Share deleted successfully"}