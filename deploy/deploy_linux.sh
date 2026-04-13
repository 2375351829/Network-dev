#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo -e "${GREEN}=== LanFileHub 部署脚本 (Linux) ===${NC}"
echo -e "${YELLOW}项目根目录: ${PROJECT_ROOT}${NC}"

# 检查Python版本
echo -e "${YELLOW}检查Python版本...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: Python 3 未安装${NC}"
    exit 1
fi

# 检查pip3
echo -e "${YELLOW}检查pip3...${NC}"
pip3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: pip3 未安装${NC}"
    exit 1
fi

# 进入后端目录
echo -e "${YELLOW}进入后端目录...${NC}"
cd "${PROJECT_ROOT}/backend" || {
    echo -e "${RED}错误: 无法进入后端目录${NC}"
    exit 1
}

# 安装后端依赖
echo -e "${YELLOW}安装后端依赖...${NC}"
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 安装后端依赖失败${NC}"
    exit 1
fi

# 初始化数据库
echo -e "${YELLOW}初始化数据库...${NC}"
python3 db/init_db.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: 数据库初始化失败，可能已存在${NC}"
fi

# 进入前端目录
echo -e "${YELLOW}进入前端目录...${NC}"
cd "${PROJECT_ROOT}/frontend" || {
    echo -e "${RED}错误: 无法进入前端目录${NC}"
    exit 1
}

# 检查npm
echo -e "${YELLOW}检查npm...${NC}"
npm --version
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: npm 未安装${NC}"
    exit 1
fi

# 安装前端依赖
echo -e "${YELLOW}安装前端依赖...${NC}"
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 安装前端依赖失败${NC}"
    exit 1
fi

# 构建前端
echo -e "${YELLOW}构建前端...${NC}"
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 构建前端失败${NC}"
    exit 1
fi

# 启动后端服务
echo -e "${YELLOW}启动后端服务...${NC}"
cd "${PROJECT_ROOT}/backend" || {
    echo -e "${RED}错误: 无法进入后端目录${NC}"
    exit 1
}

# 检查是否有环境变量文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}创建默认.env文件...${NC}"
    cat > .env << EOF
# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///lanfilehub.db

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo -e "${GREEN}默认.env文件创建成功${NC}"
fi

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
echo -e "${YELLOW}服务将在 http://0.0.0.0:8000 上运行${NC}"
echo -e "${YELLOW}API文档地址: http://0.0.0.0:8000/docs${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"

# 启动uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload