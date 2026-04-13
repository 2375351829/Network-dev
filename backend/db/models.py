from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 关系
    files = relationship("File", back_populates="user")
    shares_created = relationship("Share", back_populates="creator", foreign_keys="Share.creator_id")
    shares_received = relationship("Share", back_populates="receiver", foreign_keys="Share.receiver_id")
    messages_sent = relationship("ChatRecord", back_populates="sender", foreign_keys="ChatRecord.sender_id")
    messages_received = relationship("ChatRecord", back_populates="receiver", foreign_keys="ChatRecord.receiver_id")
    playlists = relationship("Playlist", back_populates="user")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float, nullable=False)
    file_type = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    folder_path = Column(String(500), nullable=False, default="/")
    is_public = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    file_hash = Column(String(255), nullable=True, index=True)  # 文件哈希值，用于去重
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="files")
    shares = relationship("Share", back_populates="file")

class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    share_code = Column(String(50), unique=True, nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    file = relationship("File", back_populates="shares")
    creator = relationship("User", back_populates="shares_created", foreign_keys=[creator_id])
    receiver = relationship("User", back_populates="shares_received", foreign_keys=[receiver_id])

class ChatRecord(Base):
    __tablename__ = "chat_records"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, file, image
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    read_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    sender = relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="messages_received", foreign_keys=[receiver_id])
    file = relationship("File")

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="playlists")
    playlist_items = relationship("PlaylistItem", back_populates="playlist")

class PlaylistItem(Base):
    __tablename__ = "playlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    playlist = relationship("Playlist", back_populates="playlist_items")
    file = relationship("File")

class VideoProgress(Base):
    __tablename__ = "video_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    progress = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    file = relationship("File")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 为None时表示系统级通知
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # system, file, share, chat, backup
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer, nullable=True)  # 关联的资源ID，如文件ID、共享ID等
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User")
