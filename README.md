# 多人聊天平台

一个简单的多人聊天系统，支持网页版、Windows桌面版和安卓App。

## ✨ 功能特性

- 🔐 用户注册登录（需要管理员审核）
- 💬 公共聊天大厅
- 🔒 私密消息（仅双方可见，管理员仍可见）
- 📁 文件上传（图片、视频、音频、文件）
- 👑 管理员系统（审核用户、删除消息、查看所有数据）
- 🧹 自动清理机制（超过10GB自动删除旧文件）
- 🖥️ Electron桌面版支持
- 📱 安卓App支持（WebView封装）

## 🛠️ 技术栈

- **后端**: Python + FastAPI + SQLAlchemy + SQLite
- **前端**: 原生HTML/CSS/JavaScript（无需npm）
- **桌面版**: Electron
- **安卓版**: WebView封装（原生Android项目）
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

# 5. 启动服务器（默认端口8000，可自定义）
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
├── android-app/          # 安卓App（WebView封装）
│   ├── app/              # Android应用代码
│   ├── build.gradle      # Gradle构建配置
│   └── build.sh          # 构建脚本
├── storage/              # 文件存储目录（自动创建）
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

## 📱 安卓App构建

### 前置要求

1. 安装 Android SDK（推荐通过 Android Studio 安装）
2. 设置环境变量 `ANDROID_HOME` 或 `ANDROID_SDK_ROOT`
3. 确保 `d8` 和 `aapt2` 工具在 PATH 中

### 构建步骤

```bash
# 进入安卓目录
cd android-app

# 使用构建脚本（推荐）
./build.sh

# 或手动构建
# 1. 编译资源
aapt2 compile --dir app/src/main/res -o build/resources.zip
aapt2 link -o build/apk/base.apk -I $ANDROID_HOME/platforms/android-34/android.jar \
  --manifest app/src/main/AndroidManifest.xml build/resources.zip

# 2. 编译Java代码
javac -source 1.8 -target 1.8 -bootclasspath $ANDROID_HOME/platforms/android-34/android.jar \
  -d build/obj app/src/main/java/com/chat/platform/*.java

# 3. 转换为DEX
d8 --output build/apk/ build/obj/**/*.class

# 4. 打包APK
# ... (详见build.sh脚本)
```

### 安装APK

构建完成后，APK文件位于 `android-app/output/聊天平台.apk`，可以通过以下方式安装：

1. **USB安装**: 连接手机，启用USB调试，运行 `adb install output/聊天平台.apk`
2. **文件传输**: 将APK文件传输到手机，点击安装

### 自定义配置

编辑 `android-app/app/src/main/java/com/chat/platform/MainActivity.java` 中的服务器地址：

```java
// 修改为你的服务器地址
private static final String SERVER_URL = "http://your-server-ip:8000";
```

## 🖥️ Electron桌面版构建

### 前置要求

1. 安装 Node.js 和 npm
2. 安装 Electron 依赖

### 构建步骤

```bash
# 进入Electron目录
cd electron

# 安装依赖
npm install

# 构建Windows版本
npm run build-win

# 或使用手动打包脚本
./build-manual.ps1
```

## 🔧 配置说明

### 环境变量

可以通过环境变量配置：

```bash
# 数据库URL（默认SQLite）
DATABASE_URL=sqlite+aiosqlite:///./chat.db

# JWT密钥（建议修改）
SECRET_KEY=your-secret-key-here

# 管理员密码（默认admin123456）
ADMIN_PASSWORD=your-admin-password

# 存储大小限制（默认10GB）
MAX_STORAGE_SIZE=10737418240

# 允许的CORS来源（默认*）
ALLOWED_ORIGINS=http://localhost:8000,https://your-domain.com
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

### 4. 安卓App无法连接服务器

1. 确保手机和服务器在同一网络
2. 检查服务器防火墙是否开放端口
3. 使用服务器的局域网IP地址（不是localhost）
4. 确保服务器启动时绑定 `0.0.0.0`

### 5. Electron桌面版白屏

1. 检查服务器是否正常运行
2. 确认Electron配置中的服务器地址正确
3. 查看控制台错误信息

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

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请提交Issue或联系开发者。