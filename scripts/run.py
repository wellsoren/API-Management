"""
API密钥管理器 — 可执行文件启动入口
被 PyInstaller 打包为 exe 后的实际入口点。
启动 uvicorn Web 服务器并自动打开浏览器。
"""
import os
import sys
import webbrowser
from pathlib import Path


def main():
    print("=" * 50)
    print("  API 密钥管理器 v1.0")
    print("=" * 50)
    print()

    # 切换到可执行文件所在目录（打包后）或项目根目录（开发时）
    # 这样数据库、日志等资源与 exe 同级存放
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent.parent
    os.chdir(str(app_dir))

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
