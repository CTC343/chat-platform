from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..database import UserStatus, UserRole, MessageType, MessageVisibility

# 用户创建模式
class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str

# 用户响应模式
class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: Optional[str] = None
    status: UserStatus
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户登录模式
class UserLogin(BaseModel):
    username: str
    password: str

# 管理员审核模式
class UserApproval(BaseModel):
    user_id: int
    status: UserStatus

# 消息创建模式
class MessageCreate(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    visibility: MessageVisibility = MessageVisibility.PUBLIC
    receiver_id: Optional[int] = None  # 私密消息时使用

# 消息响应模式
class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: Optional[int] = None
    content: str
    message_type: MessageType
    file_path: Optional[str] = None
    visibility: MessageVisibility
    created_at: datetime
    sender: UserResponse
    
    class Config:
        from_attributes = True

# 令牌模式
class Token(BaseModel):
    access_token: str
    token_type: str

# 令牌数据模式
class TokenData(BaseModel):
    username: Optional[str] = None

# 文件上传响应模式
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int