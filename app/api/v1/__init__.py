from fastapi import APIRouter

from api.v1.auth_router import auth_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
