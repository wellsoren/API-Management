from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session, select

import httpx

from app.db import get_session
from app.models import PRESET_PROVIDER_NAMES, PRESET_PROVIDERS, PROVIDER_CONFIG_DICTS, ApiInfo, get_provider_config

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_apis(
    request: Request,
    search: str = Query(default=""),
    provider: str = Query(default=""),
    model_name: str = Query(default=""),
    name: str = Query(default=""),
    app_usage: str = Query(default=""),
    session: Session = Depends(get_session),
):
    """搜索和筛选 API 列表，返回 HTML 片段"""
    query = select(ApiInfo)
    if search:
        query = query.where(
            ApiInfo.name.contains(search)
            | ApiInfo.url_openai.contains(search)
            | ApiInfo.url_anthropic.contains(search)
            | ApiInfo.model_name.contains(search)
            | ApiInfo.model_attr.contains(search)
            | ApiInfo.app_usage.contains(search)
        )
    if provider:
        query = query.where(ApiInfo.provider == provider)
    if model_name:
        query = query.where(ApiInfo.model_name.contains(model_name))
    if name:
        query = query.where(ApiInfo.name.contains(name))
    if app_usage:
        query = query.where(ApiInfo.app_usage.contains(app_usage))
    apis = session.exec(query).all()
    # 预置提供商 + 数据库中的额外提供商（去重合并）
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "fragments/api_table.html",
        {"apis": apis, "providers": all_providers}
    )


@router.get("/fetch-models", response_class=JSONResponse)
async def fetch_models(
    base_url: str = Query(default=""),
    api_key: str = Query(default=""),
):
    """调用提供商接口拉取模型列表（OpenAI 兼容格式）"""
    if not base_url:
        raise HTTPException(status_code=400, detail="接口地址不能为空")
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key 不能为空")
    # 构造 /models 请求地址
    models_url = base_url.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(models_url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"拉取失败，状态码 {resp.status_code}：{resp.text[:200]}"
            )
        data = resp.json()
        models = []
        # 兼容两种 API 返回格式
        if "data" in data and isinstance(data["data"], list):
            for m in data["data"]:
                mid = m.get("id", "")
                if mid:
                    models.append(mid)
        elif isinstance(data, list):
            for m in data:
                mid = m.get("id", "") if isinstance(m, dict) else str(m)
                if mid:
                    models.append(mid)
        models.sort()
        return {"models": models, "total": len(models)}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时，请检查接口地址是否正确")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"拉取失败：{str(e)[:200]}")


@router.get("/new", response_class=HTMLResponse)
async def new_api_form(request: Request, session: Session = Depends(get_session)):
    """返回新建 API 的表单 HTML 片段"""
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "fragments/api_form.html",
        {"api": None, "providers": all_providers, "provider_configs": PROVIDER_CONFIG_DICTS}
    )


@router.post("/", response_class=HTMLResponse)
async def create_api(
    request: Request,
    provider: str = Form(default=""),
    name: str = Form(...),
    url_openai: str = Form(default=""),
    url_anthropic: str = Form(default=""),
    model_name: str = Form(default=""),
    model_attr: str = Form(default=""),
    api_key: str = Form(default=""),
    app_usage: str = Form(default=""),
    website: str = Form(default=""),
    session: Session = Depends(get_session),
):
    """创建新的 API 记录"""
    api = ApiInfo(
        provider=provider,
        name=name,
        url_openai=url_openai,
        url_anthropic=url_anthropic,
        model_name=model_name,
        model_attr=model_attr,
        api_key=api_key,
        app_usage=app_usage,
        website=website,
    )
    session.add(api)
    session.commit()
    session.refresh(api)
    apis = session.exec(select(ApiInfo)).all()
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "fragments/api_table.html",
        {"apis": apis, "providers": all_providers}
    )


@router.get("/{api_id}/edit", response_class=HTMLResponse)
async def edit_api_form(
    request: Request,
    api_id: int,
    session: Session = Depends(get_session),
):
    """返回编辑 API 的表单 HTML 片段"""
    api = session.get(ApiInfo, api_id)
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "fragments/api_form.html",
        {"api": api, "providers": all_providers, "provider_configs": PROVIDER_CONFIG_DICTS}
    )


@router.put("/{api_id}", response_class=HTMLResponse)
async def update_api(
    request: Request,
    api_id: int,
    provider: str = Form(default=""),
    name: str = Form(...),
    url_openai: str = Form(default=""),
    url_anthropic: str = Form(default=""),
    model_name: str = Form(default=""),
    model_attr: str = Form(default=""),
    api_key: str = Form(default=""),
    app_usage: str = Form(default=""),
    website: str = Form(default=""),
    session: Session = Depends(get_session),
):
    """更新 API 记录"""
    api = session.get(ApiInfo, api_id)
    if not api:
        return HTMLResponse("", status_code=404)
    api.provider = provider
    api.name = name
    api.url_openai = url_openai
    api.url_anthropic = url_anthropic
    api.model_name = model_name
    api.model_attr = model_attr
    api.api_key = api_key
    api.app_usage = app_usage
    api.website = website
    session.add(api)
    session.commit()
    apis = session.exec(select(ApiInfo)).all()
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    all_providers = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return templates.TemplateResponse(
        request, "fragments/api_table.html",
        {"apis": apis, "providers": all_providers}
    )


@router.delete("/{api_id}", response_class=HTMLResponse)
async def delete_api(
    api_id: int,
    session: Session = Depends(get_session),
):
    """删除 API 记录"""
    api = session.get(ApiInfo, api_id)
    if api:
        session.delete(api)
        session.commit()
    return HTMLResponse("")
