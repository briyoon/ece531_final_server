from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Path, Body

from auth import get_device_from_token
from schemas import DeviceInDB, ThermostatReport
from models import Report
from repositories import DeviceRepository, ReportRepository
from api.v1.user_router import connection_manager

device_router = APIRouter(
    dependencies=[Depends(get_device_from_token)],
)


@device_router.get("/schedule")
async def get_device_schedule(
    current_device: Annotated[DeviceInDB, Depends(get_device_from_token)]
):
    try:
        schedule = await DeviceRepository.get_device_schedule(current_device.device_id)
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@device_router.post("/report")
async def create_report(
    current_device: Annotated[DeviceInDB, Depends(get_device_from_token)],
    report_data: Annotated[ThermostatReport, Body(title="Report data")],
):
    try:
        if current_device.user_id is None:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device is not registered to a user",
            )

        report = Report(
            user_id=current_device.user_id,
            device_id=current_device.device_id,
            temperature_celcius=report_data.temperature_celcius,
            heater_on=report_data.heater_on,
            timestamp=report_data.timestamp,
        )
        await ReportRepository.create_report(report)
        await connection_manager.send_message(
            current_device.device_id, report_data.model_dump_json()
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
