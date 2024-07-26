from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body, HTTPException, status

from auth import get_user_from_token
from schemas import UserDevice, ThermostatSchedule, UserInDB
from repositories import DeviceRepository, ReportRepository

user_router = APIRouter(
    dependencies=[Depends(get_user_from_token)],
)


@user_router.get("/device")
async def get_user_devices(
    user: Annotated[UserInDB, Depends(get_user_from_token)]
) -> list[UserDevice]:
    try:
        devices = await DeviceRepository.get_users_devices(user.user_id)
        devices_to_return = []
        for device in devices:
            schedule = None
            if device.schedule is not None:
                device.schedule = ThermostatSchedule.model_validate(device.schedule)

            devices_to_return.append(
                UserDevice(
                    user_id=device.user_id,
                    device_id=device.device_id,
                    schedule=schedule,
                )
            )
        return devices_to_return
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@user_router.get("/device/{device_id}/reports")
async def get_device_reports(device_id: Annotated[UUID, Path]):
    try:
        return await ReportRepository.get_device_reports(device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# @user_router.post("/device")
# async def register_device(
#     user: Annotated[UserSchema, Depends(get_user_from_token)], device: UUID
# ):
#     return DeviceRepository.register_device(device, user.user_id)


# @user_router.delete("/device/{device_id}")
# async def unregister_device(
#     user: Annotated[UserSchema, Depends(get_user_from_token)], device_id: int
# ):
#     return DeviceRepository.unregister_device(device_id)


@user_router.post("/device/{device_id}/schedule")
async def upload_schedule(
    device_id: Annotated[UUID, Path(title="ID of device to upload schdule")],
    schedule: Annotated[ThermostatSchedule, Body],
):
    try:
        return await DeviceRepository.update_device_schedule(device_id, schedule)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@user_router.get("/device/{device_id}/schedule")
async def get_schedule(
    device_id: Annotated[UUID, Path(title="ID of device to get schedule")]
):
    try:
        return await DeviceRepository.get_device_schedule(device_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
