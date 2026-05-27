import os, sys, uuid, base64
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, or_, and_
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func

# ========== Config ==========
SECRET_KEY = os.getenv("SECRET_KEY", "chat-platform-secret-key-2026")
ALGORITHM = "HS256"
TOKEN_EXPIRE = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fix Render-style postgres URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For Vercel, use SQLite (data resets on cold start - OK for demo)
if not DATABASE_URL or "postgresql" in DATABASE_URL:
    DATABASE_URL = "sqlite:///tmp/chat.db"

# ========== Database ==========
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    avatar = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")
    role = Column(String(20), default="user")
    created_at = Column(DateTime, server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")
    file_path = Column(String(500), nullable=True)
    file_data = Column(Text, nullable=True)
    visibility = Column(String(20), default="public")
    created_at = Column(DateTime, server_default=func.now())
    sender = relationship("User", foreign_keys=[sender_id])

# Create tables
Base.metadata.create_all(bind=engine)

# Init admin
def init_admin():
    db = SessionLocal()
    try:
        from sqlalchemy import select
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = User(
                username="admin",
                password_hash=pwd.hash(os.getenv("ADMIN_PASSWORD", "admin123456")),
                nickname="管理员",
                status="approved",
                role="admin"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

init_admin()

# ========== Auth ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(401, "无法验证凭据")
    except JWTError:
        raise HTTPException(401, "无法验证凭据")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(401, "用户不存在")
    return user

def get_active_user(user: User = Depends(get_current_user)):
    if user.status != "approved":
        raise HTTPException(400, "用户未审核通过")
    return user

def get_admin(user: User = Depends(get_active_user)):
    if user.role != "admin":
        raise HTTPException(403, "需要管理员权限")
    return user

# ========== Schemas ==========
class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserApproval(BaseModel):
    user_id: int
    status: str

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"
    visibility: str = "public"
    receiver_id: Optional[int] = None

# ========== App ==========
app = FastAPI(title="多人聊天平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Frontend HTML ==========
def get_frontend_path(filename):
    base = os.path.dirname(os.path.dirname(__file__))
    frontend = os.path.join(base, "frontend")
    path = os.path.join(frontend, filename)
    if os.path.exists(path):
        return path
    # Try public dir
    public = os.path.join(base, "public")
    path = os.path.join(public, filename)
    if os.path.exists(path):
        return path
    return None

# ========== Routes ==========
@app.get("/", response_class=HTMLResponse)
async def root():
    path = get_frontend_path("index.html")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>多人聊天平台</h1><p>前端文件未找到</p>")

@app.get("/chat.html", response_class=HTMLResponse)
async def chat_page():
    path = get_frontend_path("chat.html")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>聊天页面加载失败</h1>")

@app.get("/admin.html", response_class=HTMLResponse)
async def admin_page():
    path = get_frontend_path("admin.html")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>管理页面加载失败</h1>")

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Static files (CSS/JS)
@app.get("/css/{filename:path}", response_class=HTMLResponse)
async def serve_css(filename: str):
    for d in ["frontend/css", "public/css"]:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), d, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            media = "text/css"
            return HTMLResponse(content, headers={"Content-Type": media})
    raise HTTPException(404)

@app.get("/js/{filename:path}", response_class=HTMLResponse)
async def serve_js(filename: str):
    for d in ["frontend/js", "public/js"]:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), d, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content, headers={"Content-Type": "application/javascript"})
    raise HTTPException(404)

# User routes
@app.post("/users/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "用户名已存在")
    db_user = User(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "nickname": db_user.nickname, "status": db_user.status, "role": db_user.role}

@app.post("/users/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(401, "用户名或密码错误")
    if db_user.status != "approved":
        raise HTTPException(400, "用户未审核通过")
    token = create_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
async def get_me(user: User = Depends(get_active_user)):
    return {"id": user.id, "username": user.username, "nickname": user.nickname, "avatar": user.avatar, "status": user.status, "role": user.role, "created_at": str(user.created_at)}

@app.get("/users/pending")
async def get_pending(db: Session = Depends(get_db), user: User = Depends(get_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "nickname": u.nickname, "avatar": u.avatar, "status": u.status, "role": u.role, "created_at": str(u.created_at)} for u in users]

@app.post("/users/approve")
async def approve(approval: UserApproval, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    user = db.query(User).filter(User.id == approval.user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.status = approval.status
    db.commit()
    return {"id": user.id, "username": user.username, "nickname": user.nickname, "status": user.status, "role": user.role}

# Message routes
@app.get("/messages/latest")
async def get_messages(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_active_user)):
    from sqlalchemy import or_, and_
    messages = db.query(Message).filter(
        or_(
            Message.visibility == "public",
            and_(Message.visibility == "private", or_(Message.sender_id == user.id, Message.receiver_id == user.id))
        )
    ).order_by(Message.created_at.desc()).limit(limit).all()
    messages.reverse()
    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append({
            "id": m.id, "sender_id": m.sender_id, "receiver_id": m.receiver_id,
            "content": m.content, "message_type": m.message_type,
            "file_path": m.file_path, "visibility": m.visibility,
            "created_at": str(m.created_at),
            "sender": {"id": sender.id, "username": sender.username, "nickname": sender.nickname, "status": sender.status, "role": sender.role}
        })
    return result

@app.post("/messages/send")
async def send_message(msg: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_active_user)):
    if msg.visibility == "private" and msg.receiver_id:
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()
        if not receiver:
            raise HTTPException(404, "接收用户不存在")
    db_msg = Message(
        sender_id=user.id,
        receiver_id=msg.receiver_id if msg.visibility == "private" else None,
        content=msg.content,
        message_type=msg.message_type,
        visibility=msg.visibility
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return {
        "id": db_msg.id, "sender_id": db_msg.sender_id, "receiver_id": db_msg.receiver_id,
        "content": db_msg.content, "message_type": db_msg.message_type,
        "file_path": db_msg.file_path, "visibility": db_msg.visibility,
        "created_at": str(db_msg.created_at),
        "sender": {"id": user.id, "username": user.username, "nickname": user.nickname, "status": user.status, "role": user.role}
    }

@app.post("/messages/upload")
async def upload_file(file: UploadFile = File(...), visibility: str = "public", receiver_id: Optional[int] = None, db: Session = Depends(get_db), user: User = Depends(get_active_user)):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "文件大小超过限制")
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    msg_type = "file"
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]: msg_type = "image"
    elif ext in [".mp4", ".avi", ".mov", ".mkv"]: msg_type = "video"
    elif ext in [".mp3", ".wav", ".ogg", ".m4a"]: msg_type = "audio"
    
    file_data = base64.b64encode(content).decode("utf-8")
    db_msg = Message(
        sender_id=user.id,
        receiver_id=receiver_id if visibility == "private" else None,
        content=file.filename,
        message_type=msg_type,
        file_path=f"db://{file.filename}",
        file_data=file_data,
        visibility=visibility
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return {
        "id": db_msg.id, "sender_id": db_msg.sender_id, "receiver_id": db_msg.receiver_id,
        "content": db_msg.content, "message_type": db_msg.message_type,
        "file_path": db_msg.file_path, "visibility": db_msg.visibility,
        "created_at": str(db_msg.created_at),
        "sender": {"id": user.id, "username": user.username, "nickname": user.nickname, "status": user.status, "role": user.role}
    }

@app.get("/messages/file/{message_id}")
async def get_file(message_id: int, db: Session = Depends(get_db), user: User = Depends(get_active_user)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg or not msg.file_data:
        raise HTTPException(404, "文件不存在")
    file_content = base64.b64decode(msg.file_data)
    content_types = {"image": "image/jpeg", "video": "video/mp4", "audio": "audio/mpeg", "file": "application/octet-stream"}
    ct = content_types.get(msg.message_type, "application/octet-stream")
    return Response(content=file_content, media_type=ct)

@app.get("/messages/admin/all")
async def admin_all_messages(db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    messages = db.query(Message).order_by(Message.created_at.desc()).all()
    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append({
            "id": m.id, "sender_id": m.sender_id, "receiver_id": m.receiver_id,
            "content": m.content, "message_type": m.message_type,
            "file_path": m.file_path, "visibility": m.visibility,
            "created_at": str(m.created_at),
            "sender": {"id": sender.id, "username": sender.username, "nickname": sender.nickname, "status": sender.status, "role": sender.role}
        })
    return result

@app.delete("/messages/admin/{message_id}")
async def admin_delete_message(message_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(404, "消息不存在")
    db.delete(msg)
    db.commit()
    return {"message": "消息删除成功"}
