@echo off
echo ========================================
echo    多人聊天平台 - 启动脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

:: 进入后端目录
cd /d "%~dp0backend"

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 安装依赖失败
    pause
    exit /b 1
)

:: 创建必要的目录
if not exist "storage" mkdir storage
if not exist "storage\avatars" mkdir storage\avatars
if not exist "storage\files" mkdir storage\files

:: 启动服务器
echo.
echo ========================================
echo    服务器启动中...
echo    访问地址: http://localhost:8000
echo    管理员账号: admin / admin123456
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause