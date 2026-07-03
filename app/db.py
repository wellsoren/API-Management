import sys
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

# 打包为 exe 运行时，__file__ 在只读临时目录中，
# 数据库应存储在 exe 同级目录下的 data/ 文件夹
if getattr(sys, "frozen", False):
    DB_DIR = Path(sys.executable).resolve().parent / "data"
else:
    DB_DIR = Path(__file__).resolve().parent.parent / "data"

DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR / 'app.db'}"

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """初始化数据库，创建所有表"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
