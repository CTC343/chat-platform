@echo off
chcp 65001 >nul
title 聊天平台 - Windows便携版

echo.
echo ╔══════════════════════════════════════════╗
echo ║        💬 多人聊天平台 - 便携版          ║
echo ╚══════════════════════════════════════════╝
echo.

:: 获取当前目录
set "CURRENT_DIR=%~dp0"
set "BACKEND_DIR=%CURRENT_DIR%backend"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.11+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已就绪

:: 进入后端目录
cd /d "%BACKEND_DIR%"

:: 检查并创建虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
echo 📥 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📥 安装依赖（首次运行需要几分钟）...
    pip install -r requirements.txt -q
)

:: 创建存储目录
if not exist "storage" mkdir storage
if not exist "storage\avatars" mkdir storage\avatars
if not exist "storage\files" mkdir storage\files

:: 删除旧数据库（可选）
if exist "chat.db" (
    echo 💾 检测到已有数据库
)

echo.
echo ╔══════════════════════════════════════════╗
echo ║           🚀 服务器启动中...             ║
echo ╠══════════════════════════════════════════╣
echo ║  📍 访问地址: http://localhost:8000     ║
echo ║  👤 管理员: admin / admin123456         ║
echo ╚══════════════════════════════════════════╝
echo.

:: 自动打开浏览器
start http://localhost:8000

:: 启动服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause