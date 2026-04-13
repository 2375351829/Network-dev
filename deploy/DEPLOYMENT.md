# LanFileHub 部署文档

## 项目简介
LanFileHub 是一个局域网文件共享和管理系统，支持文件传输、聊天、备份等功能。

## 系统要求

### 硬件要求
- CPU: 至少 1 核心
- 内存: 至少 1GB
- 存储空间: 至少 100MB

### 软件要求

#### 通用要求
- Python 3.7 或更高版本
- Node.js 14 或更高版本
- npm 6 或更高版本

#### Linux 系统
- 支持的发行版: Ubuntu、Debian、CentOS、Fedora 等
- 终端支持 bash

#### Windows 系统
- 支持的版本: Windows 7 或更高版本
- 命令提示符或 PowerShell

## 部署步骤

### 1. 准备项目

首先，确保你已经获取了项目代码，进入项目根目录。

```bash
cd /path/to/lanfilehub
```

### 2. 使用部署脚本

#### Linux 系统

1. 进入部署脚本目录
   ```bash
   cd deploy
   ```

2. 运行部署脚本
   ```bash
   ./deploy_linux.sh
   ```

3. 脚本会自动执行以下操作:
   - 检查 Python 和 pip 版本
   - 安装后端依赖
   - 初始化数据库
   - 检查 npm 版本
   - 安装前端依赖
   - 构建前端
   - 创建默认环境变量文件 (如果不存在)
   - 启动后端服务

#### Windows 系统

1. 进入部署脚本目录
   ```cmd
   cd deploy
   ```

2. 运行部署脚本
   ```cmd
   deploy_windows.bat
   ```

3. 脚本会自动执行以下操作:
   - 检查 Python 和 pip 版本
   - 安装后端依赖
   - 初始化数据库
   - 检查 npm 版本
   - 安装前端依赖
   - 构建前端
   - 创建默认环境变量文件 (如果不存在)
   - 启动后端服务

### 3. 访问系统

服务启动后，你可以通过以下地址访问系统:

- 系统主页: http://localhost:8000
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## 配置说明

### 环境变量

系统使用 `.env` 文件来配置环境变量，位于后端目录。默认配置如下:

```
# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///lanfilehub.db

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 自定义配置

你可以根据需要修改 `.env` 文件中的配置:

- `HOST`: 服务器监听地址，默认为 0.0.0.0 (所有网络接口)
- `PORT`: 服务器监听端口，默认为 8000
- `DATABASE_URL`: 数据库连接字符串，默认为 SQLite 数据库
- `SECRET_KEY`: JWT 签名密钥，建议修改为随机字符串
- `ALGORITHM`: JWT 算法，默认为 HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 访问令牌过期时间，默认为 30 分钟

## 性能测试

系统提供了性能测试脚本，可以测试系统的响应时间和并发处理能力。

### 运行性能测试

1. 确保服务已经启动

2. 进入部署脚本目录
   ```bash
   cd deploy
   ```

3. 运行性能测试脚本
   ```bash
   python3 performance_test.py
   ```

4. 测试结果会显示在终端中，包括:
   - API 响应时间
   - 并发请求处理能力
   - 成功/失败请求数
   - 平均/最小/最大响应时间

## 常见问题

### 1. 端口被占用

**症状**: 启动服务时出现端口被占用的错误。

**解决方案**: 修改 `.env` 文件中的 `PORT` 配置，使用其他未被占用的端口。

### 2. 依赖安装失败

**症状**: 安装依赖时出现错误。

**解决方案**:
- 确保网络连接正常
- 确保 Python 和 npm 版本符合要求
- 尝试使用国内镜像源

### 3. 数据库初始化失败

**症状**: 数据库初始化时出现错误。

**解决方案**:
- 确保 SQLite 已安装
- 检查数据库文件权限
- 尝试删除旧的数据库文件后重新初始化

### 4. 前端构建失败

**症状**: 前端构建时出现错误。

**解决方案**:
- 确保 Node.js 和 npm 版本符合要求
- 尝试删除 `node_modules` 目录后重新安装依赖

## 一键启动

系统支持一键启动，通过运行部署脚本即可完成所有部署步骤并启动服务。

### Linux 一键启动
```bash
./deploy/deploy_linux.sh
```

### Windows 一键启动
```cmd
deploy\deploy_windows.bat
```

## 命令行运行

除了使用部署脚本，你也可以手动执行以下步骤来运行系统:

### 1. 后端运行

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python db/init_db.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 前端运行

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建前端
npm run build

# 前端构建产物会输出到 dist 目录，由后端服务提供静态文件访问
```

## 注意事项

1. 本系统主要用于局域网环境，不建议直接暴露在公网
2. 生产环境部署时，建议修改 `SECRET_KEY` 为随机字符串
3. 定期备份数据库文件 (`lanfilehub.db`)
4. 注意监控系统资源使用情况，避免资源耗尽

## 故障排查

如果遇到问题，可以查看以下日志和文件:

- 后端服务日志: 终端输出
- 前端构建日志: 终端输出
- 数据库文件: `backend/lanfilehub.db`
- 环境变量配置: `backend/.env`

## 联系支持

如果遇到无法解决的问题，请联系系统管理员或开发者。