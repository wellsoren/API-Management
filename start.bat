@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title API密钥管理器 — 便携版

echo ============================================
echo    API密钥管理器 — 一键启动
echo ============================================
echo.

:: --------------------------------------------------
:: 1. 检测 Python
:: --------------------------------------------------
set PY_CMD=python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    where py >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        set PY_CMD=py -3
    ) else (
        echo [错误] 未检测到 Python，请先安装 Python 3.10+
        echo 下载地址：https://www.python.org/downloads/
        echo.
        echo 安装时请勾选「Add Python to PATH」
        pause
        exit /b 1
    )
)

:: --------------------------------------------------
:: 2. 检查 Python 版本
:: --------------------------------------------------
%PY_CMD% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if %ERRORLEVEL% neq 0 (
    echo [错误] Python 版本需要 3.10 或更高
    %PY_CMD% --version
    pause
    exit /b 1
)

echo [1/5] 检测到 Python：%PY_CMD%
%PY_CMD% --version

:: --------------------------------------------------
:: 3. 创建 / 修复虚拟环境
:: --------------------------------------------------
echo [2/5] 正在检查虚拟环境...
if not exist ".venv\Scripts\activate.bat" (
    echo   虚拟环境不存在，正在创建...
    %PY_CMD% -m venv .venv
    if !ERRORLEVEL! neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo   虚拟环境创建成功
) else (
    echo   虚拟环境已存在
)

:: --------------------------------------------------
:: 4. 安装依赖（带缓存标记）
:: --------------------------------------------------
call .venv\Scripts\activate.bat

if exist ".venv\.deps_installed" (
    echo [3/5] 依赖已安装，跳过安装步骤
    goto :skip_install
)

echo [3/5] 正在安装依赖...

:: 升级 pip（避免旧版 pip 找不到包）
python -m pip install --upgrade pip -q
if !ERRORLEVEL! neq 0 (
    echo [警告] pip 升级失败，尝试继续...
)

pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo.
    echo [错误] 依赖安装失败
    echo 请检查网络连接，或手动运行：pip install -r requirements.txt
    pause
    exit /b 1
)
echo   依赖安装完成

:: 写入缓存标记，下次跳过安装
type nul > ".venv\.deps_installed"
:skip_install

:: --------------------------------------------------
:: 5. 验证模块可导入
:: --------------------------------------------------
echo [4/5] 正在验证应用模块...
python -c "from app.main import app; print('   ✅ 模块加载正常')" 2>&1
if !ERRORLEVEL! neq 0 (
    echo [错误] 应用模块加载失败，请检查代码完整性
    pause
    exit /b 1
)

:: --------------------------------------------------
:: 6. 启动服务
:: --------------------------------------------------
echo.
echo [5/5] 正在启动服务...
echo.
echo  ╔═══════════════════════════════════════╗
echo  ║   服务启动后请访问：                    ║
echo  ║   http://localhost:8000               ║
echo  ║                                       ║
echo  ║   按 Ctrl+C 关闭服务                    ║
echo  ╚═══════════════════════════════════════╝
echo.

:: 打开浏览器
start "" http://localhost:8000

:: 前台运行 uvicorn（窗口保持打开直到 Ctrl+C）
uvicorn app.main:app --host 0.0.0.0 --port 8000

:: 服务结束后
echo.
echo ============================================
echo    服务已停止
echo ============================================
pause
