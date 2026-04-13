@echo off

:: 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

echo %GREEN%=== LanFileHub 部署脚本 (Windows) ===%NC%

:: 检查Python版本
echo %YELLOW%检查Python版本...%NC%
python --version
if %errorlevel% neq 0 (
    echo %RED%错误: Python 未安装%NC%
    pause
    exit /b 1
)

:: 检查pip
echo %YELLOW%检查pip...%NC%
pip --version
if %errorlevel% neq 0 (
    echo %RED%错误: pip 未安装%NC%
    pause
    exit /b 1
)

:: 进入后端目录
echo %YELLOW%进入后端目录...%NC%
cd /d "%~dp0\..\backend"
if %errorlevel% neq 0 (
    echo %RED%错误: 无法进入后端目录%NC%
    pause
    exit /b 1
)

:: 安装后端依赖
echo %YELLOW%安装后端依赖...%NC%
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %RED%错误: 安装后端依赖失败%NC%
    pause
    exit /b 1
)

:: 初始化数据库
echo %YELLOW%初始化数据库...%NC%
python db\init_db.py
if %errorlevel% neq 0 (
    echo %YELLOW%警告: 数据库初始化失败，可能已存在%NC%
)

:: 进入前端目录
echo %YELLOW%进入前端目录...%NC%
cd /d "%~dp0\..\..\frontend"
if %errorlevel% neq 0 (
    echo %RED%错误: 无法进入前端目录%NC%
    pause
    exit /b 1
)

:: 检查npm
echo %YELLOW%检查npm...%NC%
npm --version
if %errorlevel% neq 0 (
    echo %RED%错误: npm 未安装%NC%
    pause
    exit /b 1
)

:: 安装前端依赖
echo %YELLOW%安装前端依赖...%NC%
npm install
if %errorlevel% neq 0 (
    echo %RED%错误: 安装前端依赖失败%NC%
    pause
    exit /b 1
)

:: 构建前端
echo %YELLOW%构建前端...%NC%
npm run build
if %errorlevel% neq 0 (
    echo %RED%错误: 构建前端失败%NC%
    pause
    exit /b 1
)

:: 启动后端服务
echo %YELLOW%启动后端服务...%NC%
cd /d "%~dp0\..\..\backend"
if %errorlevel% neq 0 (
    echo %RED%错误: 无法进入后端目录%NC%
    pause
    exit /b 1
)

:: 检查是否有环境变量文件
if not exist .env (
    echo %YELLOW%创建默认.env文件...%NC%
    (echo # 服务器配置
echo HOST=0.0.0.0
echo PORT=8000
echo.
echo # 数据库配置
echo DATABASE_URL=sqlite:///lanfilehub.db
echo.
echo # JWT配置
echo SECRET_KEY=your-secret-key-here
echo ALGORITHM=HS256
echo ACCESS_TOKEN_EXPIRE_MINUTES=30) > .env
    echo %GREEN%默认.env文件创建成功%NC%
)

:: 启动服务
echo %GREEN%启动服务...%NC%
echo %YELLOW%服务将在 http://0.0.0.0:8000 上运行%NC%
echo %YELLOW%API文档地址: http://0.0.0.0:8000/docs%NC%
echo %YELLOW%按 Ctrl+C 停止服务%NC%

:: 启动uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload