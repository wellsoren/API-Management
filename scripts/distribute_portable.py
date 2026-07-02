"""
便携版打包脚本 — 将项目打包为可分发 zip 包

用法：
    python scripts/distribute_portable.py

输出：
    dist/API密钥管理器_Portable_v1.0.zip

用户收到后解压，双击 start.bat (Windows) 或 start.sh (Mac/Linux) 即可运行。
"""

import os
import shutil
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_DIR / "dist"
VERSION = "1.0"
PACKAGE_NAME = f"API密钥管理器_Portable_v{VERSION}"

# 需要排除的文件/目录
EXCLUDE_PATTERNS = {
    ".venv",
    "__pycache__",
    ".git",
    ".gitignore",
    ".atomcode.md",
    "dist",
    "scripts",
    "*.pyc",
    ".DS_Store",
    "Thumbs.db",
}


def should_exclude(name: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def main():
    # 清理旧的 dist 目录
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    zip_path = DIST_DIR / f"{PACKAGE_NAME}.zip"
    print(f"正在打包便携版...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in PROJECT_DIR.rglob("*"):
            # 跳过排除项
            if any(part.startswith(".") and part != "." for part in file_path.relative_to(PROJECT_DIR).parts):
                if file_path.name != ".env.example":
                    continue
            if should_exclude(file_path.name):
                continue
            if any(should_exclude(p) for p in file_path.relative_to(PROJECT_DIR).parts):
                continue

            # 只打包文件（不含目录）
            if file_path.is_file():
                arcname = file_path.relative_to(PROJECT_DIR)
                zf.write(file_path, arcname)

    print(f"✅ 打包完成：{zip_path}")
    print(f"   文件大小：{zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    print("用户使用方式：")
    print(f"  1. 解压 {PACKAGE_NAME}.zip")
    print("  2. Windows: 双击 start.bat")
    print("  3. macOS/Linux: 终端运行 chmod +x start.sh && ./start.sh")
    print(f"  4. 浏览器访问 http://localhost:8000")


if __name__ == "__main__":
    main()
