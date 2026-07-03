"""
API密钥管理器 — 可执行文件启动入口
被 PyInstaller 打包为 exe 后的实际入口点。
直接导入 app 对象传给 uvicorn（避免字符串导入在 PyInstaller 中失败）。
"""
import os
import sys
import webbrowser
from pathlib import Path


def main():
    try:
        # ── 确定项目根目录 ──────────────────────────────────
        if getattr(sys, "frozen", False):
            # 打包后：exe 所在目录
            app_dir = Path(sys.executable).resolve().parent
        else:
            # 开发环境：scripts/run.py → 上一级为项目根目录
            app_dir = Path(__file__).resolve().parent.parent

        # 切换工作目录并设置模块搜索路径
        os.chdir(str(app_dir))
        sys.path.insert(0, str(app_dir))

        # ── 直接导入 app 对象 ──────────────────────────────
        # PyInstaller 在分析期会发现此导入，自动将 app.main 及其依赖打包
        from app.main import app

        port = 8000
        url = f"http://127.0.0.1:{port}"

        print("=" * 50)
        print("  API 密钥管理器 v1.0")
        print("=" * 50)
        print()
        print(f"[OK] 启动中... {url}")
        print("[OK] 浏览器自动打开（如未跳转，请手动访问上述地址）")
        print("[!] 关闭此窗口即可停止服务")
        print()

        import socket
        import threading
        import time
        import uvicorn

        # ── 后台线程启动 uvicorn ────────────────────────────
        def run_server():
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=port,
                log_config=None,   # 完全禁用 uvicorn 日志配置（避免 console=False 时 stderr 为 None 导致崩溃）
                access_log=False,
            )

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # ── 等待端口就绪（最多 10 秒） ──────────────────────
        print("[..] 等待服务就绪...")
        for _ in range(100):
            time.sleep(0.1)
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    break
            except (ConnectionRefusedError, OSError):
                pass

        print("[OK] 服务已就绪，正在打开浏览器...")
        webbrowser.open(url)

        # ── 保持主线程存活 ──────────────────────────────────
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    except Exception:
        import traceback

        traceback.print_exc()
        print("\n[!] 启动失败，窗口将在 10 秒后自动关闭...")
        import time
        time.sleep(10)


if __name__ == "__main__":
    main()
