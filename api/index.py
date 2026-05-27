import sys
import os

# 设置路径
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

# 环境变量
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///tmp/chat.db")

# 创建必要的目录
os.makedirs("storage", exist_ok=True)

from app.main import app

# Vercel会自动处理FastAPI app
