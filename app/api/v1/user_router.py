from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import UUID
import asyncio

from fastapi import APIRouter, Depends, Path, Body, HTTPException, status, Request
from sse_starlette.sse import EventSourceResponse

from auth import get_user_from_token
from schemas import UserDevice, ThermostatSchedule, UserInDB, ThermostatReport
from repositories import DeviceRepository, ReportRepository

user_router = APIRouter(
    dependencies=[Depends(get_user_from_token)],
)


# not a good place to put this but w/e
class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(set)

    async def connect(self, device_id: str, client: asyncio.Queue):
        self.active_connections[device_id].add(client)

    def disconnect(self, device_id: str, client: asyncio.Queue):
        self.active_connections[device_id].remove(client)

    async def send_message(self, device_id: str, message: str):
        for client in self.active_connections[device_id]:
            await client.put(message)


connection_manager = ConnectionManager()


@user_router.get("/device")
async def get_user_devices(
    user: Annotated[UserInDB, Depends(get_user_from_token)]
) -> list[UserDevice]:
    try:
        devices = await DeviceRepository.get_users_devices(user.user_id)
        devices_to_return = []
        for device in devices:
            try:
                schedule = ThermostatSchedule.model_validate_json(device.schedule)
            except:
                schedule = None
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


@user_router.get("/device/{device_id}")
async def get_device(device_id: Annotated[UUID, Path(title="ID of device to get")]):
    try:
        device = await DeviceRepository.get_device_by_id(device_id)
        try:
            schedule = ThermostatSchedule.model_validate_json(device.schedule)
        except:
            schedule = None
        return UserDevice(
            user_id=device.user_id,
            device_id=device.device_id,
            schedule=schedule,
        )
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


@user_router.get("/device/{device_id}/reports/stream")
async def stream_device_reports(
    request: Request,
    device_id: Annotated[UUID, Path],
    user: UserInDB = Depends(get_user_from_token),
):
    # verify that device belongs to user
    devices = await DeviceRepository.get_users_devices(user.user_id)
    if device_id not in [device.device_id for device in devices]:
        raise HTTPException(
            status_code=404, detail="User does not have a device with that ID"
        )

    client_queue = asyncio.Queue()
    await connection_manager.connect(device_id, client_queue)

    async def event_generator():
        try:
            # Fetch recent reports (e.g., last 10 minutes)
            start_time = datetime.now() - timedelta(minutes=10)
            recent_reports = await ReportRepository.get_user_device_reports_after_time(
                user.user_id, device_id, start_time
            )

            for report in recent_reports:
                report_schema = ThermostatReport(
                    temperature_celcius=report.temperature_celcius,
                    heater_on=report.heater_on,
                    timestamp=report.timestamp,
                )
                yield {"event": "historical", "data": report_schema.model_dump_json()}

            while True:
                if await request.is_disconnected():
                    break
                message = await client_queue.get()
                yield {"event": "update", "data": message}
        finally:
            connection_manager.disconnect(device_id, client_queue)

    return EventSourceResponse(event_generator())


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
    schedule: Annotated[Optional[ThermostatSchedule], Body()] = None,
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
