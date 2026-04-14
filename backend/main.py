from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lanfilehub.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="LanFileHub API",
    description="局域网文件传输助手后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 导入路由
from routers import auth, files, shares, chat, multimedia, backup, lan_broadcast, notification, users

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(files.router, prefix="/api/files", tags=["文件管理"])
app.include_router(shares.router, prefix="/api/shares", tags=["共享管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
app.include_router(multimedia.router, prefix="/api/multimedia", tags=["多媒体"])
app.include_router(backup.router, prefix="/api/backup", tags=["备份"])
app.include_router(lan_broadcast.router, prefix="/api/lan-broadcast", tags=["局域网广播"])
app.include_router(notification.router, prefix="/api/notification", tags=["通知"])

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 挂载静态文件（必须在路由之后，否则会覆盖API路由）
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    # 为前端静态文件创建单独的挂载，使用通配符处理路由
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # 如果是API路径，不处理
        if full_path.startswith("api") or full_path == "health":
            return {"detail": "Not Found"}
        # 否则返回前端文件
        file_path = os.path.join(frontend_dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        else:
            # 如果文件不存在，返回index.html，让前端处理路由
            return FileResponse(os.path.join(frontend_dist_path, "index.html"))
    # 另外挂载静态文件用于直接访问
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="frontend-assets")