from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import os
import shutil
import schedule
import time
import threading
from db.models import User, File, Notification
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# 配置
BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups")
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Pydantic模型
class BackupConfig(BaseModel):
    enabled: bool = True
    interval: str = "daily"  # daily, weekly, monthly
    backup_path: str = BACKUP_DIR
    include_all_users: bool = False

class BackupStatus(BaseModel):
    last_backup: Optional[datetime] = None
    next_backup: Optional[datetime] = None
    status: str = "idle"

# 全局变量
backup_status = {
    "last_backup": None,
    "next_backup": None,
    "status": "idle"
}
backup_config = {
    "enabled": True,
    "interval": "daily",
    "backup_path": BACKUP_DIR,
    "include_all_users": False
}

# 工具函数
def get_backup_path():
    """获取当前备份路径"""
    return backup_config["backup_path"]

def create_backup_folder():
    """创建备份文件夹"""
    backup_path = get_backup_path()
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    return backup_path

def backup_files(db: Session, user_id: Optional[int] = None):
    """执行备份操作"""
    global backup_status
    backup_status["status"] = "running"
    
    try:
        # 创建备份文件夹
        backup_path = create_backup_folder()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(backup_path, f"backup_{timestamp}")
        os.makedirs(backup_folder)
        
        # 确定要备份的文件
        query = db.query(File).filter(File.is_deleted == False)
        if user_id and not backup_config["include_all_users"]:
            query = query.filter(File.user_id == user_id)
        
        files = query.all()
        backup_count = 0
        
        # 备份文件
        for file in files:
            if os.path.exists(file.file_path):
                # 创建用户文件夹
                user_folder = os.path.join(backup_folder, f"user_{file.user_id}")
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                
                # 复制文件
                dest_path = os.path.join(user_folder, file.filename)
                shutil.copy2(file.file_path, dest_path)
                backup_count += 1
        
        # 更新备份状态
        backup_status["last_backup"] = datetime.utcnow()
        backup_status["status"] = "completed"
        
        # 计算下次备份时间
        if backup_config["interval"] == "daily":
            backup_status["next_backup"] = backup_status["last_backup"] + timedelta(days=1)
        elif backup_config["interval"] == "weekly":
            backup_status["next_backup"] = backup_status["last_backup"] + timedelta(weeks=1)
        elif backup_config["interval"] == "monthly":
            backup_status["next_backup"] = backup_status["last_backup"] + timedelta(days=30)
        
        # 创建通知
        if backup_count > 0:
            notification = Notification(
                title="备份完成",
                content=f"成功备份了 {backup_count} 个文件",
                notification_type="backup",
                is_read=False
            )
            db.add(notification)
            db.commit()
        
        return {
            "message": f"Backup completed successfully. {backup_count} files backed up.",
            "backup_folder": backup_folder
        }
        
    except Exception as e:
        backup_status["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

def run_backup_schedule():
    """运行备份定时任务"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# 初始化定时任务
def init_backup_schedule():
    """初始化备份定时任务"""
    # 清除现有任务
    schedule.clear()
    
    # 根据配置设置定时任务
    if backup_config["enabled"]:
        if backup_config["interval"] == "daily":
            schedule.every().day.at("00:00").do(lambda: backup_files(SessionLocal()))
        elif backup_config["interval"] == "weekly":
            schedule.every().sunday.at("00:00").do(lambda: backup_files(SessionLocal()))
        elif backup_config["interval"] == "monthly":
            schedule.every().month.at("00:00").do(lambda: backup_files(SessionLocal()))
    
    # 启动定时任务线程
    backup_thread = threading.Thread(target=run_backup_schedule, daemon=True)
    backup_thread.start()

# 路由
@router.post("/config")
async def set_backup_config(
    config: BackupConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """设置备份配置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    global backup_config
    backup_config = config.dict()
    
    # 重新初始化定时任务
    init_backup_schedule()
    
    return {"message": "Backup configuration updated successfully", "config": backup_config}

@router.get("/config")
async def get_backup_config(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取备份配置"""
    return backup_config

@router.post("/run")
async def run_backup(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """手动执行备份"""
    if not current_user.is_admin:
        # 普通用户只能备份自己的文件
        result = backup_files(db, current_user.id)
    else:
        # 管理员可以备份所有文件
        result = backup_files(db)
    
    return result

@router.get("/status")
async def get_backup_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取备份状态"""
    return backup_status

@router.get("/list")
async def list_backups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出所有备份"""
    backup_path = get_backup_path()
    if not os.path.exists(backup_path):
        return []
    
    backups = []
    for item in os.listdir(backup_path):
        item_path = os.path.join(backup_path, item)
        if os.path.isdir(item_path):
            try:
                # 解析时间戳
                timestamp_str = item.replace("backup_", "")
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                # 计算备份大小
                total_size = 0
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                
                backups.append({
                    "name": item,
                    "timestamp": timestamp,
                    "size": total_size,
                    "path": item_path
                })
            except Exception:
                pass
    
    # 按时间戳排序
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return backups

# 导入SessionLocal
from main import SessionLocal

# 初始化备份定时任务
init_backup_schedule()