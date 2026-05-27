@echo off
chcp 65001 >nul
title 打包Windows桌面版

echo.
echo ╔══════════════════════════════════════════╗
echo ║     🖥️ 打包Windows桌面版                 ║
echo ╚══════════════════════════════════════════╝
echo.

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js
    echo    请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js已就绪

:: 进入electron目录
cd /d "%~dp0electron"

:: 检查并安装依赖
if not exist "node_modules" (
    echo 📦 安装依赖...
    npm install
)

:: 安装打包工具
echo 🔧 安装打包工具...
npm install electron-builder --save-dev

:: 开始打包
echo.
echo 🚀 开始打包Windows版本...
echo    这可能需要几分钟，请耐心等待...
echo.

npm run build:win

echo.
if exist "dist\聊天平台 Setup*.exe" (
    echo ✅ 打包完成！
    echo.
    echo 📁 打包文件位置:
    echo    %cd%\dist\
    echo.
    echo 📦 安装包: 聊天平台 Setup 1.0.0.exe
    echo.
    echo 💡 使用说明:
    echo    1. 运行安装包
    echo    2. 启动聊天平台
    echo    3. 确保后端服务器已启动
    echo.
    explorer dist
) else (
    echo ❌ 打包失败，请检查错误信息
)

pause