@echo off
cd /d D:\聊天项目\backend
del /f chat.db 2>nul
echo Database deleted.
echo Starting server...
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 9999
pause
