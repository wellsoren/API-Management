#!/usr/bin/env bash
set -e

# ============================================
#   API密钥管理器 — 一键启动脚本 (macOS/Linux)
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "   API密钥管理器 — 一键启动"
echo "============================================"
echo ""

# 检测 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python 3，请先安装 Python 3.10+"
    echo "  macOS: brew install python"
    echo "  Ubuntu: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# 检查 Python 版本
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[检测] Python 版本: $PY_VER"

python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || {
    echo "[错误] Python 版本需要 3.10 或更高，当前: $PY_VER"
    exit 1
}

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "[1/4] 正在创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活并安装依赖
echo "[2/4] 正在安装依赖..."
source .venv/bin/activate
pip install -q -r requirements.txt

# 启动服务
echo "[3/4] 正在启动服务..."
echo ""

# 打开浏览器（macOS 用 open，Linux 用 xdg-open）
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 2 && open http://localhost:8000) &
elif command -v xdg-open &> /dev/null; then
    (sleep 2 && xdg-open http://localhost:8000) &
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000

echo "[4/4] 服务已停止"
