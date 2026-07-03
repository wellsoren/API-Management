"""
API密钥管理器 — 可执行文件启动入口
被 PyInstaller 打包为 exe 后的实际入口点。
启动 uvicorn Web 服务器并自动打开浏览器。
"""
import os
import sys
import webbrowser
from pathlib import Path


def ensure_vendor_files():
    """
    确保静态资源目录中存在 vendor JS 文件。
    打包后这些文件与 exe 一起分发（已含在 data 目录中），
    此处做一次检查兜底。
    """
    # 打包后运行的临时目录（PyInstaller 解压目录）
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent

    vendor_src = base / "app" / "static" / "vendor"
    # 如果 vendor 目录不存在，尝试从 app/static 同级目录复制
    if not vendor_src.exists():
        vendor_src.mkdir(parents=True, exist_ok=True)

    # 目标目录：优先使用 exe 同级目录下的 app/static/vendor（持久化）
    exe_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else base
    vendor_dst = exe_dir / "app" / "static" / "vendor"
    vendor_dst.mkdir(parents=True, exist_ok=True)

    vendor_files = {
        "htmx.min.js": "https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js",
        "alpine.min.js": "https://unpkg.com/alpinejs@3.14.8/dist/cdn.min.js",
    }

    for name, url in vendor_files.items():
        dst_file = vendor_dst / name
        if not dst_file.exists():
            # 先从打包的数据目录复制
            src_file = vendor_src / name
            if src_file.exists():
                import shutil
                shutil.copy2(src_file, dst_file)
                print(f"[OK] 已复制: {name}")
            else:
                # 尝试从网络下载
                try:
                    import urllib.request
                    print(f"[..] 正在下载: {name} ...")
                    urllib.request.urlretrieve(url, str(dst_file))
                    print(f"[OK] 下载完成: {name}")
                except Exception as e:
                    print(f"[!] 无法下载 {name}（离线环境）: {e}")


def main():
    print("=" * 50)
    print("  API 密钥管理器 v1.0")
    print("=" * 50)
    print()

    # 确保 vendor JS 文件存在
    ensure_vendor_files()

    # 启动 uvicorn
    import uvicorn

    port = 8000
    print(f"[OK] 服务启动中... http://localhost:{port}")
    print("[OK] 浏览器自动打开（如未跳转，请手动访问上述地址）")
    print("[!] 关闭此窗口即可停止服务")
    print()

    # 延迟打开浏览器（等服务器就绪）
    import threading

    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # 切换到可执行文件所在目录（打包后）或项目根目录（开发时）
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent.parent
    os.chdir(str(app_dir))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        log_config=None,  # 避免打包后 stderr 为 None 导致日志配置崩溃
    )


if __name__ == "__main__":
    main()
