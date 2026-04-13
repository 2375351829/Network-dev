from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
import bcrypt
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lanfilehub.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 初始化管理员用户
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建管理员用户
            password = "admin123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                username="admin",
                password_hash=hashed_password,
                nickname="管理员",
                email="admin@example.com",
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("管理员用户创建成功: 用户名: admin, 密码: admin123")
        else:
            print("管理员用户已存在")
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()