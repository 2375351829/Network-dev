from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import User, File, Playlist, PlaylistItem, VideoProgress
from main import get_db
import os
from datetime import datetime
from typing import Optional

router = APIRouter()

# 多媒体文件上传
@router.post("/upload")
async def upload_media(
    file: UploadFile = FastAPIFile(...),
    folder_path: str = Form("/"),
    db: Session = Depends(get_db)
):
    # 检查文件类型
    media_types = ["audio", "video"]
    if not any(file.content_type.startswith(media_type) for media_type in media_types):
        raise HTTPException(status_code=400, detail="只支持音频和视频文件")
    
    # 确保上传目录存在
    upload_dir = os.path.join("uploads", "media")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 创建文件记录
    new_file = File(
        filename=file.filename,
        file_path=file_path,
        file_size=len(content) / (1024 * 1024),  # 转换为MB
        file_type=file.content_type,
        user_id=1,  # 暂时使用固定用户ID，实际应该从认证中获取
        folder_path=folder_path
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return {"file_id": new_file.id, "filename": new_file.filename, "message": "上传成功"}

# 获取媒体文件列表
@router.get("/list")
def get_media_list(
    media_type=None,  # audio 或 video
    db: Session = Depends(get_db)
):
    query = db.query(File).filter(File.is_deleted == False)
    
    if media_type:
        query = query.filter(File.file_type.startswith(media_type))
    
    files = query.all()
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "file_path": file.file_path,
            "file_size": file.file_size,
            "file_type": file.file_type,
            "created_at": file.created_at
        }
        for file in files
    ]

# 歌单管理

# 创建歌单
@router.post("/playlists")
def create_playlist(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db)
):
    new_playlist = Playlist(
        name=name,
        user_id=1,  # 暂时使用固定用户ID
        description=description,
        is_public=is_public
    )
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    return {"playlist_id": new_playlist.id, "name": new_playlist.name, "message": "歌单创建成功"}

# 获取歌单列表
@router.get("/playlists")
def get_playlists(db: Session = Depends(get_db)):
    playlists = db.query(Playlist).filter(Playlist.user_id == 1).all()  # 暂时使用固定用户ID
    return [
        {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "is_public": playlist.is_public,
            "created_at": playlist.created_at
        }
        for playlist in playlists
    ]

# 获取歌单详情
@router.get("/playlists/{playlist_id}")
def get_playlist_detail(
    playlist_id: int,
    db: Session = Depends(get_db)
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    items = db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist_id).order_by(PlaylistItem.order_index).all()
    return {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "is_public": playlist.is_public,
        "created_at": playlist.created_at,
        "items": [
            {
                "id": item.id,
                "file_id": item.file_id,
                "filename": item.file.filename,
                "file_type": item.file.file_type,
                "order_index": item.order_index
            }
            for item in items
        ]
    }

# 添加歌曲到歌单
@router.post("/playlists/{playlist_id}/items")
def add_item_to_playlist(
    playlist_id: int,
    file_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # 检查歌单是否存在
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    
    # 检查文件是否存在
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查文件是否已经在歌单中
    existing_item = db.query(PlaylistItem).filter(
        and_(PlaylistItem.playlist_id == playlist_id, PlaylistItem.file_id == file_id)
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="文件已在歌单中")
    
    # 获取当前最大的order_index
    max_order = db.query(PlaylistItem).filter(
        PlaylistItem.playlist_id == playlist_id
    ).count()
    
    new_item = PlaylistItem(
        playlist_id=playlist_id,
        file_id=file_id,
        order_index=max_order
    )
    db.add(new_item)
    db.commit()
    return {"message": "添加成功"}

# 从歌单中移除歌曲
@router.delete("/playlists/{playlist_id}/items/{item_id}")
def remove_item_from_playlist(
    playlist_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(PlaylistItem).filter(
        and_(PlaylistItem.id == item_id, PlaylistItem.playlist_id == playlist_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="歌曲不在歌单中")
    
    db.delete(item)
    db.commit()
    return {"message": "移除成功"}

# 视频进度记忆

# 获取视频进度
@router.get("/video-progress/{file_id}")
def get_video_progress(
    file_id: int,
    db: Session = Depends(get_db)
):
    progress = db.query(VideoProgress).filter(
        and_(VideoProgress.user_id == 1, VideoProgress.file_id == file_id)
    ).first()
    
    if progress:
        return {"file_id": file_id, "progress": progress.progress}
    else:
        return {"file_id": file_id, "progress": 0.0}

# 更新视频进度
@router.post("/video-progress/{file_id}")
def update_video_progress(
    file_id: int,
    progress: float = Form(...),
    db: Session = Depends(get_db)
):
    # 检查文件是否存在
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查是否已存在进度记录
    existing_progress = db.query(VideoProgress).filter(
        and_(VideoProgress.user_id == 1, VideoProgress.file_id == file_id)
    ).first()
    
    if existing_progress:
        existing_progress.progress = progress
        db.commit()
    else:
        new_progress = VideoProgress(
            user_id=1,
            file_id=file_id,
            progress=progress
        )
        db.add(new_progress)
        db.commit()
    
    return {"message": "进度更新成功"}
