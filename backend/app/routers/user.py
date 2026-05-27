from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import os
import uuid
from ..database import get_db, User, UserStatus, UserRole
from ..schemas.user import UserCreate, UserResponse, UserLogin, UserApproval, Token
from ..auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user,
    get_current_active_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["用户"])

# 用户注册
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    db_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        nickname=user.nickname,
        status=UserStatus.PENDING,
        role=UserRole.USER
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

# 用户登录
@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    # 查询用户
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if db_user.status != UserStatus.APPROVED:
        raise HTTPException(status_code=400, detail="用户未审核通过")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# 管理员：获取待审核用户
@router.get("/pending", response_model=list[UserResponse])
async def get_pending_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    result = await db.execute(
        select(User).where(User.status == UserStatus.PENDING)
    )
    return result.scalars().all()

# 管理员：审核用户
@router.post("/approve", response_model=UserResponse)
async def approve_user(
    approval: UserApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # 查询用户
    result = await db.execute(select(User).where(User.id == approval.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新状态
    user.status = approval.status
    await db.commit()
    await db.refresh(user)
    
    return user

# 上传头像
@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 创建存储目录
    os.makedirs("storage/avatars", exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"storage/avatars/{filename}"
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 更新用户头像
    current_user.avatar = file_path
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

# 管理员：初始化管理员账号
@router.post("/init-admin")
async def init_admin(db: AsyncSession = Depends(get_db)):
    # 检查是否已存在管理员
    result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    if result.scalar_one_or_none():
        return {"message": "管理员已存在"}
    
    # 创建管理员
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123456"),
        nickname="管理员",
        status=UserStatus.APPROVED,
        role=UserRole.ADMIN
    )
    
    db.add(admin_user)
    await db.commit()
    
    return {"message": "管理员创建成功"}