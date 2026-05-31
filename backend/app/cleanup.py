import os
import asyncio
from datetime import datetime
from sqlalchemy import select, func
from .database import async_session, Message

# 存储目录
STORAGE_DIR = "storage"
# 最大存储大小 (20GB)
MAX_STORAGE_SIZE = 20 * 1024 * 1024 * 1024

async def get_storage_size():
    """获取存储目录总大小"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(STORAGE_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size

async def get_old_messages(limit=100):
    """获取最旧的消息"""
    async with async_session() as db:
        result = await db.execute(
            select(Message)
            .where(Message.file_path.isnot(None))
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

async def delete_message_and_file(message):
    """删除消息及其关联文件"""
    # 删除文件
    if message.file_path and os.path.exists(message.file_path):
        try:
            os.remove(message.file_path)
            print(f"已删除文件: {message.file_path}")
        except OSError as e:
            print(f"删除文件失败: {message.file_path}, 错误: {e}")
    
    # 删除数据库记录
    async with async_session() as db:
        await db.delete(message)
        await db.commit()
        print(f"已删除消息: {message.id}")

async def cleanup_storage():
    """清理存储空间"""
    print(f"[{datetime.now()}] 开始检查存储空间...")
    
    current_size = await get_storage_size()
    print(f"当前存储大小: {current_size / (1024*1024*1024):.2f} GB")
    
    if current_size <= MAX_STORAGE_SIZE:
        print("存储空间正常，无需清理")
        return
    
    print(f"存储空间超过限制，开始清理...")
    
    # 获取旧消息
    old_messages = await get_old_messages(100)
    
    deleted_count = 0
    for message in old_messages:
        await delete_message_and_file(message)
        deleted_count += 1
        
        # 检查是否已清理足够空间
        current_size = await get_storage_size()
        if current_size <= MAX_STORAGE_SIZE * 0.8:  # 清理到80%以下
            break
    
    print(f"清理完成，已删除 {deleted_count} 条消息")
    print(f"清理后存储大小: {current_size / (1024*1024*1024):.2f} GB")

async def start_cleanup_task():
    """启动清理任务"""
    print("启动存储清理任务...")
    
    while True:
        try:
            await cleanup_storage()
        except Exception as e:
            print(f"清理任务出错: {e}")
        
        # 每小时检查一次
        await asyncio.sleep(3600)