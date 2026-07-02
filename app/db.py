from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

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
