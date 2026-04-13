from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
import os
import shutil
import uuid
import json
import hashlib
from db.models import User, File
from main import get_db
from routers.auth import get_current_active_user

# 路由
router = APIRouter()

# 配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Pydantic模型
class FileBase(BaseModel):
    filename: str
    folder_path: str = "/"
    is_public: bool = False

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    file_path: str
    file_size: float
    file_type: str
    user_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FileRename(BaseModel):
    new_filename: str

class FileMove(BaseModel):
    new_folder_path: str

# 工具函数
def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def get_file_type(filename: str) -> str:
    ext = get_file_extension(filename)
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "image"
    elif ext in [".mp4", ".avi", ".mov", ".wmv", ".flv"]:
        return "video"
    elif ext in [".mp3", ".wav", ".flac", ".ogg"]:
        return "audio"
    elif ext in [".pdf"]:
        return "pdf"
    elif ext in [".doc", ".docx"]:
        return "word"
    elif ext in [".xls", ".xlsx"]:
        return "excel"
    elif ext in [".ppt", ".pptx"]:
        return "powerpoint"
    elif ext in [".txt", ".md", ".json", ".xml", ".html", ".css", ".js"]:
        return "text"
    else:
        return "other"

def calculate_file_hash(file_path: str) -> str:
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 分块读取文件
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 路由
@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_path: str = "/",
    is_public: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 获取文件类型
    file_type = get_file_type(file.filename)
    
    # 计算文件哈希值
    file_hash = calculate_file_hash(file_path)
    
    # 检查是否存在重复文件
    existing_file = db.query(File).filter(
        File.file_hash == file_hash,
        File.is_deleted == False
    ).first()
    
    if existing_file:
        # 如果存在重复文件，删除新上传的文件并返回现有文件
        os.remove(file_path)
        return existing_file
    
    # 创建文件记录
    db_file = File(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        file_hash=file_hash,
        user_id=current_user.id,
        folder_path=folder_path,
        is_public=is_public
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file

@router.get("/list", response_model=list[FileResponse])
async def list_files(
    folder_path: str = "/",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取用户的文件
    files = db.query(File).filter(
        File.user_id == current_user.id,
        File.is_deleted == False,
        File.folder_path == folder_path
    ).all()
    
    # 如果是管理员，还可以看到所有公开文件
    if current_user.is_admin:
        public_files = db.query(File).filter(
            File.is_public == True,
            File.is_deleted == False
        ).all()
        files.extend(public_files)
    
    return files

@router.get("/user/download/{file_id}")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    if not (file.user_id == current_user.id or file.is_public or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 检查文件是否存在
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type="application/octet-stream"
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    if not (file.user_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 标记为删除
    file.is_deleted = True
    file.updated_at = datetime.utcnow()
    db.commit()
    
    # 可选：删除物理文件
    # if os.path.exists(file.file_path):
    #     os.remove(file.file_path)
    
    return {"message": "File deleted successfully"}

@router.put("/{file_id}/rename")
async def rename_file(
    file_id: int,
    file_rename: FileRename,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    if not (file.user_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 更新文件名
    file.filename = file_rename.new_filename
    file.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(file)
    
    return file

@router.put("/{file_id}/move")
async def move_file(
    file_id: int,
    file_move: FileMove,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    if not (file.user_id == current_user.id or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 更新文件夹路径
    file.folder_path = file_move.new_folder_path
    file.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(file)
    
    return file

# OnlyOffice集成
@router.get("/{file_id}/edit")
async def edit_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查权限
    has_permission = False
    
    # 1. 文件所有者
    if file.user_id == current_user.id:
        has_permission = True
    # 2. 管理员
    elif current_user.is_admin:
        has_permission = True
    # 3. 共享用户
    else:
        from db.models import Share
        # 检查是否有共享记录
        share = db.query(Share).filter(
            Share.file_id == file_id,
            Share.receiver_id == current_user.id
        ).first()
        if share:
            has_permission = True
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 构建OnlyOffice配置
    document = {
        "fileType": os.path.splitext(file.filename)[1][1:],
        "key": f"{file.id}_{datetime.utcnow().timestamp()}",
        "title": file.filename,
        "url": f"http://localhost:8000/api/files/{file_id}/download",
        "callbackUrl": f"http://localhost:8000/api/files/{file_id}/onlyoffice-callback"
    }
    
    editorConfig = {
        "user": {
            "id": str(current_user.id),
            "name": current_user.username
        },
        "lang": "zh-CN",
        "mode": "edit",
        "collaborative": True,
        "canCoedit": True
    }
    
    config = {
        "document": document,
        "editorConfig": editorConfig
    }
    
    return {
        "config": config,
        "onlyoffice_url": "http://localhost:8080/web-apps/apps/documenteditor/main/index.html"
    }

@router.post("/{file_id}/onlyoffice-callback")
async def onlyoffice_callback(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # 解析回调数据
    data = await request.json()
    
    # 检查状态
    if data.get("status") == 2:  # 编辑完成
        # 获取文件内容
        try:
            import requests
            download_url = data.get("url")
            if download_url:
                response = requests.get(download_url)
                response.raise_for_status()
                
                # 更新文件
                file = db.query(File).filter(File.id == file_id).first()
                if file:
                    with open(file.file_path, "wb") as f:
                        f.write(response.content)
                    file.updated_at = datetime.utcnow()
                    db.commit()
        except Exception as e:
            print(f"Error saving file from OnlyOffice: {e}")
    
    # 返回成功响应
    return JSONResponse(content={"error": 0})

@router.get("/{file_id}/download")
async def download_file_for_onlyoffice(
    file_id: int,
    db: Session = Depends(get_db)
):
    # 获取文件
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 检查文件是否存在
    if not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename
    )

@router.get("/duplicates")
async def find_duplicate_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """查找重复文件"""
    # 查找用户的所有非删除文件
    files = db.query(File).filter(
        File.user_id == current_user.id,
        File.is_deleted == False,
        File.file_hash.isnot(None)
    ).all()
    
    # 按哈希值分组
    hash_groups = {}
    for file in files:
        if file.file_hash not in hash_groups:
            hash_groups[file.file_hash] = []
        hash_groups[file.file_hash].append(file)
    
    # 找出重复的文件组
    duplicates = []
    for hash_value, file_list in hash_groups.items():
        if len(file_list) > 1:
            duplicates.append({
                "hash": hash_value,
                "files": file_list
            })
    
    return duplicates

@router.delete("/duplicates/clean")
async def clean_duplicate_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """清理重复文件（保留第一个文件，删除其他重复文件）"""
    # 查找用户的所有非删除文件
    files = db.query(File).filter(
        File.user_id == current_user.id,
        File.is_deleted == False,
        File.file_hash.isnot(None)
    ).order_by(File.created_at).all()
    
    # 按哈希值分组
    hash_groups = {}
    for file in files:
        if file.file_hash not in hash_groups:
            hash_groups[file.file_hash] = []
        hash_groups[file.file_hash].append(file)
    
    deleted_count = 0
    for hash_value, file_list in hash_groups.items():
        if len(file_list) > 1:
            # 保留第一个文件，删除其他文件
            for file in file_list[1:]:
                # 标记为删除
                file.is_deleted = True
                file.updated_at = datetime.utcnow()
                deleted_count += 1
    
    db.commit()
    
    return {"message": f"Cleaned {deleted_count} duplicate files"}