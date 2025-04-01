from fastapi import APIRouter

from .routes import router

auth_router = APIRouter()

auth_router.include_router(router)
