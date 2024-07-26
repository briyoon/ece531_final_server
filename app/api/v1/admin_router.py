from typing import Annotated
from uuid import UUID
import base64

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body

from auth import get_admin_user, get_password_hash
from repositories import DeviceRepository, UserRepository
from schemas import DeviceInDB, UserInDB, CreateUser, CreateDevice, RegisterDevice
from models import User, Device

admin_router = APIRouter(
    dependencies=[Depends(get_admin_user)],
)


@admin_router.post("/device")
async def create_device(
    new_device: Annotated[CreateDevice, Body(title="New device data")]
):
    try:
        device = Device(
            device_id=new_device.device_id,
            public_key=base64.b64decode(new_device.public_key_b64).decode(),
        )
        await DeviceRepository.create_device(device)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/device")
async def get_all_devices():
    try:
        return await DeviceRepository.get_all_devices()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/device/{device_id}")
async def get_device(device_id: Annotated[UUID, Path(title="ID of device to get")]):
    try:
        return await DeviceRepository.get_device_by_id(device_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.put("/device/{device_id}")
async def update_device(
    device_id: Annotated[UUID, Path(title="ID of device to update")],
    device: Annotated[DeviceInDB, Body(title="Updated device data")],
):
    try:
        await DeviceRepository.update_device(device_id, device)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.delete("/device/{device_id}")
async def delete_device(
    device_id: Annotated[UUID, Path(title="ID of device to delete")]
):
    try:
        await DeviceRepository.delete_device_by_id(device_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.post("/device/register")
async def register_device(
    register_data: Annotated[RegisterDevice, Body(title="Data to register a device")]
):
    try:
        await DeviceRepository.register_device(
            register_data.device_id, register_data.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.delete("/device/unregister")
async def unregister_device(
    device_id: Annotated[RegisterDevice, Body(title="Data to unregister a device")]
):
    try:
        await DeviceRepository.unregister_device(device_id.device_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.post("/user")
async def create_user(new_user: Annotated[CreateUser, Body(title="New user data")]):
    try:
        user = User(
            email=new_user.email,
            hashed_password=get_password_hash(new_user.password),
            is_admin=new_user.is_admin,
        )
        await UserRepository.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/user")
async def get_all_users():
    try:
        return await UserRepository.get_all_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.get("/user/{user_id}")
async def get_user(user_id: Annotated[UUID, Path(title="ID of user to get")]):
    try:
        return await UserRepository.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.put("/user/{user_id}")
async def update_user(
    user_id: Annotated[UUID, Path(title="ID of user to update")],
    user_data: Annotated[UserInDB, Body(title="Updated user data")],
):
    try:
        UserRepository.update_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@admin_router.delete("/user/{user_id}")
async def delete_user(user_id: Annotated[UUID, Path(title="ID of user to delete")]):
    try:
        UserRepository.delete_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
