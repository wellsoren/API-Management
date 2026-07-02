from fastapi import APIRouter
from app.routers.apis import router as apis_router

api_router = APIRouter()
api_router.include_router(apis_router, prefix="/api/v1/apis", tags=["apis"])
