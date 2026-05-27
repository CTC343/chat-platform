from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os
import uuid
import base64
from ..database import get_db, Message, User, MessageType, MessageVisibility
from ..schemas.user import MessageCreate, MessageResponse, UserResponse
from ..auth import get_current_active_user, get_current_admin

router = APIRouter(prefix="/messages", tags=["消息"])

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",  # 图片
    ".mp4", ".avi", ".mov", ".mkv",  # 视频
    ".mp3", ".wav", ".ogg", ".m4a",  # 音频
    ".pdf", ".doc", ".docx", ".txt", ".zip", ".rar"  # 文档
}

# 获取最新消息（HTTP轮询）
@router.get("/latest", response_model=List[MessageResponse])
async def get_latest_messages(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 查询公开消息和当前用户相关的私密消息
    query = (
        select(Message)
        .options(selectinload(Message.sender))
        .where(
            or_(
                Message.visibility == MessageVisibility.PUBLIC,
                and_(
                    Message.visibility == MessageVisibility.PRIVATE,
                    or_(
                        Message.sender_id == current_user.id,
                        Message.receiver_id == current_user.id
                    )
                )
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 按时间正序返回
    return list(reversed(messages))

# 发送消息
@router.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 如果是私密消息，检查接收者是否存在
    if message.visibility == MessageVisibility.PRIVATE and message.receiver_id:
        result = await db.execute(select(User).where(User.id == message.receiver_id))
        receiver = result.scalar_one_or_none()
        if not receiver:
            raise HTTPException(status_code=404, detail="接收用户不存在")
    
    # 创建消息
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id if message.visibility == MessageVisibility.PRIVATE else None,
        content=message.content,
        message_type=message.message_type,
        visibility=message.visibility
    )
    
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    
    # 重新查询以获取关联数据
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender))
        .where(Message.id == db_message.id)
    )
    return result.scalar_one()

# 上传文件并发送消息
@router.post("/upload", response_model=MessageResponse)
async def upload_file(
    file: UploadFile = File(...),
    message_type: MessageType = MessageType.FILE,
    visibility: MessageVisibility = MessageVisibility.PUBLIC,
    receiver_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过限制（最大10MB）")
    
    # 检查文件类型
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if file_ext and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 将文件内容编码为base64存储到数据库
    file_data_base64 = base64.b64encode(content).decode("utf-8")
    
    # 根据文件扩展名确定消息类型
    if message_type == MessageType.FILE:
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            message_type = MessageType.IMAGE
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            message_type = MessageType.VIDEO
        elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            message_type = MessageType.AUDIO
    
    # 创建消息（文件数据存储在数据库中）
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id if visibility == MessageVisibility.PRIVATE else None,
        content=file.filename,
        message_type=message_type,
        file_path=f"db://{file.filename}",  # 标记为数据库存储
        file_data=file_data_base64,
        visibility=visibility
    )
    
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    
    # 重新查询以获取关联数据
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender))
        .where(Message.id == db_message.id)
    )
    return result.scalar_one()

# 获取文件数据（从数据库）
@router.get("/file/{message_id}")
async def get_file_data(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    if not message.file_data:
        raise HTTPException(status_code=404, detail="文件数据不存在")
    
    # 返回base64编码的文件数据
    import base64
    file_content = base64.b64decode(message.file_data)
    
    from fastapi.responses import Response
    # 根据消息类型设置Content-Type
    content_types = {
        "image": "image/jpeg",
        "video": "video/mp4",
        "audio": "audio/mpeg",
        "file": "application/octet-stream"
    }
    content_type = content_types.get(message.message_type, "application/octet-stream")
    
    return Response(content=file_content, media_type=content_type)

# 管理员：获取所有消息
@router.get("/admin/all", response_model=List[MessageResponse])
async def get_all_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender))
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()

# 管理员：删除消息
@router.delete("/admin/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    await db.delete(message)
    await db.commit()
    
    return {"message": "消息删除成功"}
