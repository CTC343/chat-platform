from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio
from .database import create_tables
from .routers import user, message
from .cleanup import start_cleanup_task

# 创建FastAPI应用
app = FastAPI(
    title="多人聊天平台",
    description="一个简单的多人聊天系统",
    version="1.0.0"
)

# 配置CORS - 支持公网访问
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
os.makedirs("storage", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# 挂载前端静态文件
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

# 包含路由
app.include_router(user.router)
app.include_router(message.router)

# 启动事件
@app.on_event("startup")
async def startup_event():
    # 创建数据库表
    await create_tables()
    
    # 初始化管理员账号
    from .database import async_session, User, UserRole, UserStatus
    from sqlalchemy import select
    from .auth import get_password_hash
    
    async with async_session() as db:
        # 检查是否已存在管理员
        result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        if not result.scalar_one_or_none():
            # 创建管理员
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123456")
            admin_user = User(
                username="admin",
                password_hash=get_password_hash(admin_password),
                nickname="管理员",
                status=UserStatus.APPROVED,
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            await db.commit()
    
    # 启动清理任务
    asyncio.create_task(start_cleanup_task())

# 首页
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

# 聊天页面
@app.get("/chat.html")
async def chat_page():
    return FileResponse(os.path.join(frontend_dir, "chat.html"))

# 管理页面
@app.get("/admin.html")
async def admin_page():
    return FileResponse(os.path.join(frontend_dir, "admin.html"))

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
