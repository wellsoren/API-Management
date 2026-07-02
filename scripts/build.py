"""
跨平台可执行文件打包脚本 — API密钥管理器

用法：
    # 打包当前平台可执行文件
    python scripts/build.py

    # 指定平台（仅用于生成打包命令说明，实际需在目标平台执行）
    python scripts/build.py --platform windows|macos|linux

依赖：
    pip install pyinstaller

输出：
    dist/API密钥管理器/  (目录，包含可执行文件 + 资源文件)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_DIR / "dist"
SPEC_FILE = PROJECT_DIR / "scripts" / "build.spec"

SYSTEM = platform.system()  # Windows / Darwin / Linux


def check_dependencies():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller  # noqa
    except ImportError:
        print("[!] 未安装 PyInstaller，正在安装...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            cwd=PROJECT_DIR,
        )
        print("[✓] PyInstaller 安装完成")


def build():
    """执行打包"""
    check_dependencies()

    # 清理旧的 dist
    target_name = f"API密钥管理器_v1.0_{SYSTEM.lower()}"
    target_dir = DIST_DIR / target_name
    if target_dir.exists():
        shutil.rmtree(target_dir)

    print(f"============================================")
    print(f"  打包平台: {SYSTEM}")
    print(f"  输出目录: {target_dir}")
    print(f"============================================")
    print()

    # 执行 PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(SPEC_FILE),
        "--distpath", str(target_dir),
        "--workpath", str(PROJECT_DIR / "build"),
        "--clean",
        "--noconfirm",
    ]

    print(f"执行: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=PROJECT_DIR)

    # 清理临时 build 目录
    build_dir = PROJECT_DIR / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)

    print()
    print(f"[✓] 打包完成！")
    print(f"    可执行文件位置: {target_dir}/")

    # 显示不同平台的可执行文件路径
    if SYSTEM == "Windows":
        print(f"    可执行文件: {target_dir}/API密钥管理器/API密钥管理器.exe")
        print(f"    调试版: {target_dir}/API密钥管理器/API密钥管理器_调试版.exe")
    elif SYSTEM == "Darwin":
        print(f"    应用包: {target_dir}/API密钥管理器/API密钥管理器.app")
    else:
        print(f"    可执行文件: {target_dir}/API密钥管理器/API密钥管理器")


def print_cross_platform_guide():
    """打印跨平台打包指引"""
    print()
    print("=" * 60)
    print("  跨平台打包指引")
    print("=" * 60)
    print()
    print("  PyInstaller 无法交叉编译，需要在目标平台上分别打包：")
    print()
    print("  Windows:")
    print("    cd api_management")
    print("    python scripts\\build.py")
    print()
    print("  macOS:")
    print("    cd api_management")
    print("    python3 scripts/build.py")
    print()
    print("  Linux:")
    print("    cd api_management")
    print("    python3 scripts/build.py")
    print()
    print("  或者使用 CI/CD（如 GitHub Actions）自动化三平台打包。")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="API密钥管理器 — 可执行文件打包")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux"],
        help="指定目标平台（仅用于展示打包命令，实际需在目标平台执行）",
    )
    args = parser.parse_args()

    if args.platform:
        print(f"[信息] 指定平台: {args.platform}")
        print("[信息] PyInstaller 不支持交叉编译，请在对应平台上运行本脚本。")
        print()
        print_cross_platform_guide()
        return

    build()
    print_cross_platform_guide()


if __name__ == "__main__":
    main()
