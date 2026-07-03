# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 — API密钥管理器

生成两个版本：
  1. console 版（调试用，显示控制台窗口）
  2. windowed 版（发布用，隐藏控制台窗口）

用法：
    pyinstaller scripts/build.spec --distpath dist/API密钥管理器_v1.0_windows --clean --noconfirm
"""

import os
import sys
from pathlib import Path

# ── 项目根目录（spec 文件所在目录的上级） ──────────────────────────
# 注意：PyInstaller exec() 执行 spec 文件，没有 __file__
# 用 SPEC 变量（PyInstaller 提供）：spec 文件绝对路径
PROJECT_DIR = Path(os.path.dirname(SPEC)).parent

# ── 数据文件：templates 和 static ────────────────────────────────
def collect_data_files(src_dir: str, dest: str) -> list:
    """递归收集目录下的所有文件，返回 (源路径, 目标路径) 列表"""
    src = Path(src_dir)
    if not src.exists():
        print(f"[WARN] 数据目录不存在: {src}")
        return []
    result = []
    for f in src.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src)
            result.append((str(f), str(Path(dest) / rel.parent)))
    return result

# 收集模板和静态文件
datas = []
datas.extend(collect_data_files(str(PROJECT_DIR / "app" / "templates"), "app/templates"))
datas.extend(collect_data_files(str(PROJECT_DIR / "app" / "static"), "app/static"))

# ── 隐藏导入（PyInstaller 有时会遗漏的包） ────────────────────────
hiddenimports = [
    "app",
    "app.routers",
    "app.templates",
    "app.templates.fragments",
    "sqlmodel",
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "httpx",
    "httpx._transports.default",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "sniffio",
    "h11",
    "httpcore",
    "httpcore._backends",
    "httpcore._backends.sync",
    "idna",
    "multipart",
    "pydantic",
    "pydantic_core",
    "jinja2",
    "markupsafe",
    "starlette",
    "starlette.middleware",
    "starlette.staticfiles",
    "starlette.templating",
]

# ── 排除不必要的包以减小体积 ──────────────────────────────────────
excludes = [
    "tkinter",
    "matplotlib",
    "scipy",
    "PIL",
    "cv2",
    "numpy",
    "pandas",
    "notebook",
    "jupyter",
    "setuptools",
    "pip",
    "wheel",
    "pywin32",
    "IPython",
    "lxml",
]

# ── 关键：处理路径中的空格 ────────────────────────────────────────
# PyInstaller 的 spec 文件内部路径用 str 表示，已有空格时 Python 原生支持

block_cipher = None

# ================================================================
# 控制台版（调试用）
# ================================================================
a = Analysis(
    [str(PROJECT_DIR / "scripts" / "run.py")],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe_console = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="API密钥管理器_调试版",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ================================================================
# 窗口版（发布用 — 默认不显示控制台）
# ================================================================
exe_windowed = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="API密钥管理器",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
