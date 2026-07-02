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

# --------------------------------------------------
# 1. 检测 Python
# --------------------------------------------------
PY_CMD=""

if command -v python3 &> /dev/null; then
    PY_CMD="python3"
elif command -v python &> /dev/null; then
    PY_CMD="python"
else
    echo "[错误] 未检测到 Python 3，请先安装 Python 3.10+"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# --------------------------------------------------
# 2. 检查 Python 版本
# --------------------------------------------------
echo "[1/5] 检测到 Python: $($PY_CMD --version 2>&1)"

$PY_CMD -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || {
    echo "[错误] Python 版本需要 3.10 或更高"
    $PY_CMD --version
    exit 1
}

# --------------------------------------------------
# 3. 创建 / 修复虚拟环境
# --------------------------------------------------
echo "[2/5] 正在检查虚拟环境..."

if [ ! -f ".venv/bin/activate" ]; then
    echo "   虚拟环境不存在，正在创建..."
    $PY_CMD -m venv .venv
    echo "   虚拟环境创建成功"
else
    echo "   虚拟环境已存在"
fi

# --------------------------------------------------
# 4. 安装依赖（带缓存标记）
# --------------------------------------------------
source .venv/bin/activate

if [ -f ".venv/.deps_installed" ]; then
    echo "[3/5] 依赖已安装，跳过安装步骤"
else
    echo "[3/5] 正在安装依赖..."

    # 升级 pip
    python -m pip install --upgrade pip -q 2>/dev/null || echo "   [警告] pip 升级失败，尝试继续..."

    pip install -r requirements.txt || {
        echo ""
        echo "[错误] 依赖安装失败"
        echo "请检查网络连接，或手动运行：pip install -r requirements.txt"
        exit 1
    }
    echo "   依赖安装完成"

    # 写入缓存标记，下次跳过安装
    touch .venv/.deps_installed
fi

# --------------------------------------------------
# 5. 验证模块可导入
# --------------------------------------------------
echo "[4/5] 正在验证应用模块..."
python -c "from app.main import app; print('   ✅ 模块加载正常')" 2>&1 || {
    echo "[错误] 应用模块加载失败，请检查代码完整性"
    exit 1
}

# --------------------------------------------------
# 6. 启动服务
# --------------------------------------------------
echo ""
echo "[5/5] 正在启动服务..."
echo ""
echo "============================================"
echo "   服务启动后请访问：http://localhost:8000"
echo "   按 Ctrl+C 关闭服务"
echo "============================================"
echo ""

# 打开浏览器（macOS 用 open，Linux 用 xdg-open）
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 2 && open http://localhost:8000) 2>/dev/null &
elif command -v xdg-open &> /dev/null; then
    (sleep 2 && xdg-open http://localhost:8000) 2>/dev/null &
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000

echo ""
echo "============================================"
echo "   服务已停止"
echo "============================================"
