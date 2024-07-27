import asyncio
from collections import defaultdict
from fastapi import APIRouter

from api.v1.auth_router import auth_router
from api.v1.admin_router import admin_router
from api.v1.user_router import user_router
from api.v1.device_router import device_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(admin_router, prefix="/admin", tags=["admin"])
v1_router.include_router(user_router, prefix="/user", tags=["user"])
v1_router.include_router(device_router, prefix="/device", tags=["device"])
