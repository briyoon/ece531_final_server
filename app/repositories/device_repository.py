from uuid import UUID
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update

from schemas import ThermostatSchedule
from models import Device
from database import get_db


class DeviceRepository:
    """Stateless collection of DB access functions for Device model"""

    @staticmethod
    async def create_device(device: Device):
        async with get_db() as session:
            try:
                session.add(device)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def get_users_devices(user_id: UUID) -> list[Device]:
        async with get_db() as session:
            try:
                stmt = select(Device).filter(Device.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    @staticmethod
    async def get_device_by_id(device_id: UUID):
        async with get_db() as session:
            try:
                device = await session.get(Device, device_id)
                if device is not None:
                    assert isinstance(device, Device)
                    return device
                raise ValueError(f"Device with id {device_id} not found")
            except SQLAlchemyError as e:
                raise e

    @staticmethod
    async def delete_device_by_id(device_id: UUID):
        async with get_db() as session:
            try:
                device = await session.get(Device, device_id)
                if device is None:
                    raise ValueError(f"Device with id {device_id} not found")
                await session.delete(device)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def update_device(device_id: UUID, device: Device):
        async with get_db() as session:
            try:
                stmt = (
                    update(Device).where(Device.device_id == device_id).values(**device)
                )
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def register_device(device_id: UUID, user_id: UUID):
        async with get_db() as session:
            try:
                stmt = (
                    update(Device)
                    .where(Device.device_id == device_id)
                    .values(user_id=user_id, register_timestamp=datetime.now())
                )
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def unregister_device(device_id: UUID):
        async with get_db() as session:
            try:
                stmt = (
                    update(Device)
                    .where(Device.device_id == device_id)
                    .values(user_id=None)
                )
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def update_device_schedule(
        device_id: UUID, schedule: ThermostatSchedule | None
    ):
        async with get_db() as session:
            try:
                if schedule is None:
                    schedule_json = None
                else:
                    schedule_json = schedule.model_dump_json()
                stmt = (
                    update(Device)
                    .where(Device.device_id == device_id)
                    .values(schedule=schedule_json)
                )
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def get_device_schedule(device_id: UUID):
        async with get_db() as session:
            try:
                stmt = select(Device.schedule).filter(Device.device_id == device_id)
                result = await session.execute(stmt)
                schedule_json = result.scalars().first()
                try:
                    return ThermostatSchedule.model_validate_json(schedule_json)
                except:
                    return None
            except SQLAlchemyError as e:
                raise e

    @staticmethod
    async def get_all_devices() -> list[Device]:
        async with get_db() as session:
            try:
                stmt = select(Device)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e
