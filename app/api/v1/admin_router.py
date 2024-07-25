from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body

from auth import get_admin_user
from repositories import DeviceRepository, UserRepository
from schemas import DeviceSchema, UserSchema

admin_router = APIRouter()


@admin_router.post("/admin/device")
async def create_device(
    device: Annotated[DeviceSchema, Body(title="New device data")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        await DeviceRepository.create_device(device)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/admin/device")
async def get_all_devices(current_user: UserSchema = Depends(get_admin_user)):
    try:
        return await DeviceRepository.get_all_devices()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/admin/device/{device_id}")
async def get_device(
    device_id: Annotated[UUID, Path(title="ID of device to get")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        return await DeviceRepository.get_device_by_id(device_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.put("/admin/device/{device_id}")
async def update_device(
    device_id: Annotated[UUID, Path(title="ID of device to update")],
    device: Annotated[DeviceSchema, Body(title="Updated device data")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        DeviceRepository.update_device(device_id, device)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.delete("/admin/device/{device_id}")
async def delete_device(
    device_id: Annotated[UUID, Path(title="ID of device to delete")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        DeviceRepository.delete_device_by_id(device_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.post("/admin/user")
async def create_user(
    new_user: Annotated[UserSchema, Body(title="New user data")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        await UserRepository.create_user(new_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/admin/user")
async def get_all_users(current_user: UserSchema = Depends(get_admin_user)):
    try:
        return await UserRepository.get_all_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/admin/user/{user_id}")
async def get_user(
    user_id: Annotated[UUID, Path(title="ID of user to get")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        return await UserRepository.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.put("/admin/user/{user_id}")
async def update_user(
    user_id: Annotated[UUID, Path(title="ID of user to update")],
    user_data: Annotated[UserSchema, Body(title="Updated user data")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        UserRepository.update_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.delete("/admin/user/{user_id}")
async def delete_user(
    user_id: Annotated[UUID, Path(title="ID of user to delete")],
    current_user: UserSchema = Depends(get_admin_user),
):
    try:
        UserRepository.delete_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
