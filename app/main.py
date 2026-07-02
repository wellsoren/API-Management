from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db import engine, init_db

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="API 接口管理工具", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    with Session(engine) as session:
        from app.models import ApiInfo, PRESET_PROVIDER_NAMES, PRESET_PROVIDERS

        apis = session.query(ApiInfo).all()
        total = len(apis)
        # 预置提供商（字符串） + 数据库中的额外提供商（去重合并）
        db_providers = session.query(ApiInfo.provider).distinct().all()
        db_set = {p[0] for p in db_providers if p[0]}
        all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "index.html",
        {
            "apis": apis,
            "total": total,
            "providers": all_providers,
            "provider_configs": [{"name": p.name, "base_url_openai": p.base_url_openai, "base_url_anthropic": p.base_url_anthropic, "website": p.website} for p in PRESET_PROVIDERS],
        }
    )


# 注册业务路由
from app.routers import api_router
app.include_router(api_router)
