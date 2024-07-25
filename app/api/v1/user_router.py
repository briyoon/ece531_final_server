from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from auth import get_user_from_token
from schemas import UserSchema
from repositories import DeviceRepository, ReportRepository

user_router = APIRouter()


@user_router.get("/device")
async def get_user_devices(user: Annotated[UserSchema, Depends(get_user_from_token)]):
    return DeviceRepository.get_users_devices(user.user_id)


@user_router.get("/device/{device_id}/reports")
async def get_device_reports(
    user: Annotated[UserSchema, Depends(get_user_from_token)], device_id: int
):
    return ReportRepository.get_device_reports(device_id)


@user_router.post("/device")
async def register_device(
    user: Annotated[UserSchema, Depends(get_user_from_token)], device: UUID
):
    return DeviceRepository.register_device(device, user.user_id)


@user_router.delete("/device/{device_id}")
async def unregister_device(
    user: Annotated[UserSchema, Depends(get_user_from_token)], device_id: int
):
    return DeviceRepository.unregister_device(device_id)


@user_router.post("/device/{device_id}/schedule")
async def upload_schedule(
    user: Annotated[UserSchema, Depends(get_user_from_token)], device_id: int
):
    return DeviceRepository.upload_schedule(device_id)


@user_router.get("/device/{device_id}/schedule")
async def get_schedule(
    user: Annotated[UserSchema, Depends(get_user_from_token)], device_id: int
):
    return DeviceRepository.get_schedule(device_id)
