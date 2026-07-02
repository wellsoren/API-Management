@echo off
chcp 65001 >nul
title API密钥管理器 — 便携版

echo ============================================
echo    API密钥管理器 — 一键启动
echo ============================================
echo.

:: 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 Python 版本
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if %ERRORLEVEL% neq 0 (
    echo [错误] Python 版本需要 3.10 或更高
    pause
    exit /b 1
)

:: 创建虚拟环境（如果不存在）
if not exist ".venv" (
    echo [1/4] 正在创建虚拟环境...
    python -m venv .venv
)

:: 激活虚拟环境
echo [2/4] 正在安装依赖...
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: 启动服务
echo [3/4] 正在启动服务...
echo.

:: 在后台启动 uvicorn，并打开浏览器
start "" http://localhost:8000
uvicorn app.main:app --host 0.0.0.0 --port 8000

:: 如果用户关闭服务
echo.
echo [4/4] 服务已停止
pause
