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
    dist/API密钥管理器_v1.0_<平台>/API密钥管理器/  (目录，含可执行文件 + 资源文件)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_DIR / "dist"
SPEC_FILE = PROJECT_DIR / "scripts" / "build.spec"
RUN_SCRIPT = PROJECT_DIR / "scripts" / "run.py"

SYSTEM = platform.system()  # Windows / Darwin / Linux

# 需要下载的 vendor JS 文件
VENDOR_FILES = {
    "htmx.min.js": "https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js",
    "alpine.min.js": "https://unpkg.com/alpinejs@3.14.8/dist/cdn.min.js",
}


def check_dependencies():
    """检查 PyInstaller 是否已安装"""
    try:
        import PyInstaller  # noqa
    except ImportError:
        print("[!] 未安装 PyInstaller，正在安装...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            cwd=str(PROJECT_DIR),
        )
        print("[OK] PyInstaller 安装完成")


def ensure_vendor_files():
    """下载 vendor JS 文件到 app/static/vendor/，确保打包时能包含"""
    vendor_dir = PROJECT_DIR / "app" / "static" / "vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)

    for name, url in VENDOR_FILES.items():
        dst = vendor_dir / name
        if dst.exists():
            print(f"  [OK] {name} 已存在")
            continue
        print(f"  [..] 正在下载 {name} ...", end=" ", flush=True)
        try:
            urllib.request.urlretrieve(url, str(dst))
            print("[OK]")
        except Exception as e:
            print(f"[FAIL] 下载失败: {e}")
            print(f"  [!] 请手动下载 {url} 到 {dst}")


def build():
    """执行打包"""
    check_dependencies()

    print()
    print("=" * 60)
    print(f"  打包平台: {SYSTEM}")
    print(f"  输出目录: {DIST_DIR}")
    print("=" * 60)
    print()

    # 1. 下载 vendor JS 文件
    print("[1/3] 下载前端依赖...")
    ensure_vendor_files()
    print()

    # 2. 检查 spec 文件存在
    if not SPEC_FILE.exists():
        print(f"[FAIL] 错误: spec 文件不存在: {SPEC_FILE}")
        print("[!] 请确保 scripts/build.spec 已创建")
        sys.exit(1)

    if not RUN_SCRIPT.exists():
        print(f"[FAIL] 错误: 启动脚本不存在: {RUN_SCRIPT}")
        print("[!] 请确保 scripts/run.py 已创建")
        sys.exit(1)

    # 3. 清理旧的构建目录
    print("[2/3] 清理旧构建...")
    build_dir = PROJECT_DIR / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)

    target_name = f"API密钥管理器_v1.0_{SYSTEM.lower()}"
    target_dir = DIST_DIR / target_name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    print()

    # 4. 执行 PyInstaller
    #    关键：Windows 路径含空格时，用 str() 传给 subprocess，
    #    subprocess 会正确处理（因为它接收的是列表，不是 shell 字符串）
    print("[3/3] 执行 PyInstaller 打包...")
    print(f"  Spec 文件: {SPEC_FILE}")
    print(f"  目标路径: {target_dir}")
    print()

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(SPEC_FILE),
        "--distpath",
        str(target_dir),
        "--workpath",
        str(PROJECT_DIR / "build"),
        "--clean",
        "--noconfirm",
    ]

    print(f"  执行命令:")
    # 显示时用引号包裹含空格的路径以便用户理解
    display_cmd = []
    for part in cmd:
        if " " in part:
            display_cmd.append(f'"{part}"')
        else:
            display_cmd.append(part)
    print(f"    {' '.join(display_cmd)}")
    print()

    try:
        subprocess.check_call(cmd, cwd=str(PROJECT_DIR))
    except subprocess.CalledProcessError as e:
        print()
        print("[FAIL] 打包失败!")
        print(f"    退出码: {e.returncode}")
        print()
        print("可能的原因及解决方案:")
        print("  1. 网络问题 — 确认 vendor JS 文件已下载到 app/static/vendor/")
        print("  2. 缺少依赖 — 运行: pip install -r requirements.txt")
        print("  3. 磁盘空间不足 — 释放空间后重试")
        print("  4. 权限问题 — 以管理员身份运行")
        print()
        print("手动排查:")
        print(f"  cd {PROJECT_DIR}")
        print(f"  {' '.join(cmd)}")
        sys.exit(1)

    # 5. 清理临时 build 目录
    if build_dir.exists():
        shutil.rmtree(build_dir)

    print()
    print("[OK] 打包完成！")
    print()

    # 6. 显示输出文件
    if SYSTEM == "Windows":
        print(f"  主程序:     {target_dir / 'API密钥管理器.exe'}")
        print(f"  调试版:     {target_dir / 'API密钥管理器_调试版.exe'}")
        print(f"  目录总大小: {get_dir_size(target_dir):.1f} MB")
    elif SYSTEM == "Darwin":
        app_dir = target_dir
        print(f"  App Bundle: {app_dir / 'API密钥管理器.app'}")
        print()
        print("  注意: macOS 需要执行以下命令以移除隔离属性:")
        print(f"    xattr -cr {app_dir / 'API密钥管理器.app'}")
        print(f"  目录总大小: {get_dir_size(target_dir):.1f} MB")
    else:
        exe_path = target_dir / "API密钥管理器"
        print(f"  可执行文件: {exe_path}")
        if exe_path.exists():
            os.chmod(str(exe_path), 0o755)
            print(f"  目录总大小: {get_dir_size(target_dir):.1f} MB")


def get_dir_size(path: Path) -> float:
    """计算目录大小（MB）"""
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total / 1024 / 1024


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
    print("  或使用 CI/CD 自动化打包。")
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
