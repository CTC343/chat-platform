#!/bin/bash

echo "========================================"
echo "    多人聊天平台 - 启动脚本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/backend"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "安装依赖失败"
    exit 1
fi

# 创建必要的目录
mkdir -p storage/avatars storage/files

# 启动服务器
echo
echo "========================================"
echo "    服务器启动中..."
echo "    访问地址: http://localhost:8000"
echo "    管理员账号: admin / admin123456"
echo "========================================"
echo

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload