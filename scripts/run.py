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

        # 先打开浏览器（等 uvicorn 就绪后再开可能会因阻塞错过）
        webbrowser.open(url)

        # ── 启动 uvicorn（传 app 对象，而非字符串） ──────────
        import uvicorn

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="critical",  # 只显示 CRITICAL 级别的错误
            access_log=False,      # 不输出请求日志
        )
    except Exception:
        import traceback

        traceback.print_exc()
        print("\n[!] 启动失败，窗口将在 10 秒后自动关闭...")
        import time
        time.sleep(10)


if __name__ == "__main__":
    main()
