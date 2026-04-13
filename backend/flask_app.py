from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import User, File, Playlist, PlaylistItem, VideoProgress
from main import engine
import os
from datetime import datetime

app = Flask(__name__)

# 依赖项
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# 多媒体文件上传
@app.route("/api/multimedia/upload", methods=["POST"])
async def upload_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # 检查文件类型
    media_types = ["audio", "video"]
    if not any(file.content_type.startswith(media_type) for media_type in media_types):
        return jsonify({"error": "只支持音频和视频文件"}), 400
    
    # 确保上传目录存在
    upload_dir = os.path.join("uploads", "media")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)
    
    # 创建文件记录
    db = next(get_db())
    new_file = File(
        filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path) / (1024 * 1024),  # 转换为MB
        file_type=file.content_type,
        user_id=1,  # 暂时使用固定用户ID，实际应该从认证中获取
        folder_path=request.form.get("folder_path", "/")
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return jsonify({"file_id": new_file.id, "filename": new_file.filename, "message": "上传成功"})

# 获取媒体文件列表
@app.route("/api/multimedia/list", methods=["GET"])
def get_media_list():
    media_type = request.args.get("media_type")
    db = next(get_db())
    
    query = db.query(File).filter(File.is_deleted == False)
    
    if media_type:
        query = query.filter(File.file_type.startswith(media_type))
    
    files = query.all()
    return jsonify([
        {
            "id": file.id,
            "filename": file.filename,
            "file_path": file.file_path,
            "file_size": file.file_size,
            "file_type": file.file_type,
            "created_at": file.created_at.isoformat()
        }
        for file in files
    ])

# 歌单管理

# 创建歌单
@app.route("/api/multimedia/playlists", methods=["POST"])
def create_playlist():
    name = request.form.get("name")
    if not name:
        return jsonify({"error": "歌单名称不能为空"}), 400
    
    description = request.form.get("description")
    is_public = request.form.get("is_public", "false").lower() == "true"
    
    db = next(get_db())
    new_playlist = Playlist(
        name=name,
        user_id=1,  # 暂时使用固定用户ID
        description=description,
        is_public=is_public
    )
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    return jsonify({"playlist_id": new_playlist.id, "name": new_playlist.name, "message": "歌单创建成功"})

# 获取歌单列表
@app.route("/api/multimedia/playlists", methods=["GET"])
def get_playlists():
    db = next(get_db())
    playlists = db.query(Playlist).filter(Playlist.user_id == 1).all()  # 暂时使用固定用户ID
    return jsonify([
        {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "is_public": playlist.is_public,
            "created_at": playlist.created_at.isoformat()
        }
        for playlist in playlists
    ])

# 获取歌单详情
@app.route("/api/multimedia/playlists/<int:playlist_id>", methods=["GET"])
def get_playlist_detail(playlist_id):
    db = next(get_db())
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        return jsonify({"error": "歌单不存在"}), 404
    
    items = db.query(PlaylistItem).filter(PlaylistItem.playlist_id == playlist_id).order_by(PlaylistItem.order_index).all()
    return jsonify({
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "is_public": playlist.is_public,
        "created_at": playlist.created_at.isoformat(),
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
    })

# 添加歌曲到歌单
@app.route("/api/multimedia/playlists/<int:playlist_id>/items", methods=["POST"])
def add_item_to_playlist(playlist_id):
    file_id = request.form.get("file_id")
    if not file_id:
        return jsonify({"error": "文件ID不能为空"}), 400
    
    file_id = int(file_id)
    db = next(get_db())
    
    # 检查歌单是否存在
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        return jsonify({"error": "歌单不存在"}), 404
    
    # 检查文件是否存在
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404
    
    # 检查文件是否已经在歌单中
    existing_item = db.query(PlaylistItem).filter(
        and_(PlaylistItem.playlist_id == playlist_id, PlaylistItem.file_id == file_id)
    ).first()
    if existing_item:
        return jsonify({"error": "文件已在歌单中"}), 400
    
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
    return jsonify({"message": "添加成功"})

# 从歌单中移除歌曲
@app.route("/api/multimedia/playlists/<int:playlist_id>/items/<int:item_id>", methods=["DELETE"])
def remove_item_from_playlist(playlist_id, item_id):
    db = next(get_db())
    item = db.query(PlaylistItem).filter(
        and_(PlaylistItem.id == item_id, PlaylistItem.playlist_id == playlist_id)
    ).first()
    if not item:
        return jsonify({"error": "歌曲不在歌单中"}), 404
    
    db.delete(item)
    db.commit()
    return jsonify({"message": "移除成功"})

# 视频进度记忆

# 获取视频进度
@app.route("/api/multimedia/video-progress/<int:file_id>", methods=["GET"])
def get_video_progress(file_id):
    db = next(get_db())
    progress = db.query(VideoProgress).filter(
        and_(VideoProgress.user_id == 1, VideoProgress.file_id == file_id)
    ).first()
    
    if progress:
        return jsonify({"file_id": file_id, "progress": progress.progress})
    else:
        return jsonify({"file_id": file_id, "progress": 0.0})

# 更新视频进度
@app.route("/api/multimedia/video-progress/<int:file_id>", methods=["POST"])
def update_video_progress(file_id):
    progress = request.form.get("progress")
    if not progress:
        return jsonify({"error": "进度不能为空"}), 400
    
    progress = float(progress)
    db = next(get_db())
    
    # 检查文件是否存在
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        return jsonify({"error": "文件不存在"}), 404
    
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
    
    return jsonify({"message": "进度更新成功"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
