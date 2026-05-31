import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
import enum

# 从环境变量读取数据库URL，支持PostgreSQL和SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chat.db")

# 修复Render的PostgreSQL URL格式（postgres:// -> postgresql+asyncpg://）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# 创建异步引擎
if "sqlite" in DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)

# 创建异步会话
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 创建基类
Base = declarative_base()

# 用户状态枚举
class UserStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# 用户角色枚举
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    avatar = Column(String(500), nullable=True)
    status = Column(String(20), default=UserStatus.PENDING)
    role = Column(String(20), default=UserRole.USER)
    muted = Column(Integer, default=0)  # 0=正常, 1=禁言
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 消息类型枚举
class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"

# 消息可见性枚举
class MessageVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

# 消息模型
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default=MessageType.TEXT)
    file_path = Column(String(500), nullable=True)
    file_data = Column(Text, nullable=True)  # Base64编码的文件数据
    visibility = Column(String(20), default=MessageVisibility.PUBLIC)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    sender = relationship("User", foreign_keys=[sender_id])

# 依赖注入：获取数据库会话
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# 创建数据库表
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
