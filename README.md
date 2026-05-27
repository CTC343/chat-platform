# 多人聊天平台

一个简单的多人聊天系统，支持网页版和Windows桌面版。

## ✨ 功能特性

- 🔐 用户注册登录（需要管理员审核）
- 💬 公共聊天大厅
- 🔒 私密消息（仅双方可见，管理员仍可见）
- 📁 文件上传（图片、视频、音频、文件）
- 👑 管理员系统（审核用户、删除消息、查看所有数据）
- 🧹 自动清理机制（超过10GB自动删除旧文件）
- 🖥️ Electron桌面版支持

## 🛠️ 技术栈

- **后端**: Python + FastAPI + SQLAlchemy + SQLite
- **前端**: 原生HTML/CSS/JavaScript（无需npm）
- **桌面版**: Electron
- **UI**: 深色模式，类似Discord风格
- **容器化**: Docker支持

## 🚀 快速开始

### 方式一：直接运行（推荐）

#### Windows
```cmd
# 双击运行 start.bat
start.bat
```

#### Linux/Mac
```bash
# 添加执行权限
chmod +x start.sh

# 运行脚本
./start.sh
```

### 方式二：手动启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方式三：Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 🔑 默认账号

- **管理员**: admin / admin123456

## 📁 项目结构

```
聊天项目/
├── backend/              # 后端代码
│   ├── app/              # FastAPI应用
│   │   ├── main.py       # 主应用
│   │   ├── database.py   # 数据库模型
│   │   ├── auth.py       # 认证模块
│   │   ├── cleanup.py    # 自动清理
│   │   └── routers/      # API路由
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端代码
│   ├── index.html        # 登录页面
│   ├── chat.html         # 聊天页面
│   ├── admin.html        # 管理页面
│   ├── css/              # 样式文件
│   └── js/               # JavaScript文件
├── electron/             # Electron桌面版
│   ├── main.js           # 主进程
│   ├── index.html        # 桌面应用页面
│   └── package.json      # Electron配置
├── storage/              # 文件存储目录
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker编排
├── start.bat             # Windows启动脚本
├── start.sh              # Linux/Mac启动脚本
└── README.md             # 项目说明
```

## 🔌 API接口

### 用户相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /users/register | 用户注册 |
| POST | /users/login | 用户登录 |
| GET | /users/me | 获取当前用户信息 |
| GET | /users/pending | 获取待审核用户（管理员） |
| POST | /users/approve | 审核用户（管理员） |
| POST | /users/avatar | 上传头像 |

### 消息相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /messages/latest | 获取最新消息 |
| POST | /messages/send | 发送消息 |
| POST | /messages/upload | 上传文件并发送消息 |
| GET | /messages/admin/all | 获取所有消息（管理员） |
| DELETE | /messages/admin/{id} | 删除消息（管理员） |

## 🖥️ 访问地址

启动后访问：
- **网页版**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📝 开发说明

### 核心功能

1. **用户系统**
   - 注册需要管理员审核
   - 支持头像上传
   - JWT令牌认证

2. **聊天功能**
   - 公共大厅消息
   - 私密消息（UI隔离）
   - 文件上传（图片/视频/音频/文件）
   - 每2秒轮询更新

3. **管理员功能**
   - 审核注册用户
   - 查看所有消息
   - 删除消息

4. **自动清理**
   - 监控storage目录大小
   - 超过10GB自动删除旧文件
   - 每小时检查一次

### 技术特点

- **无需npm**: 前端使用原生HTML/CSS/JS，无需构建工具
- **异步支持**: 后端使用FastAPI异步框架
- **SQLite数据库**: 轻量级，无需额外安装
- **JWT认证**: 安全的用户认证机制
- **自动清理**: 防止存储空间溢出

## 🔧 配置说明

### 环境变量

可以通过环境变量配置：

```bash
# 数据库URL（默认SQLite）
DATABASE_URL=sqlite+aiosqlite:///./chat.db

# JWT密钥（建议修改）
SECRET_KEY=your-secret-key-here

# 存储大小限制（默认10GB）
MAX_STORAGE_SIZE=10737418240
```

### 修改配置

编辑 `backend/app/database.py` 修改数据库配置
编辑 `backend/app/auth.py` 修改JWT密钥
编辑 `backend/app/cleanup.py` 修改清理策略

## 🐛 常见问题

### 1. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 2. 数据库损坏
```bash
# 删除数据库文件重新开始
rm chat.db
```

### 3. 权限问题
```bash
# 确保storage目录有写权限
chmod -R 755 storage/
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请提交Issue或联系开发者。