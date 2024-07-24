from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update

from models import Device
from database import get_db


class DeviceRepository:
    """Stateless collection of DB access functions for Device model"""

    async def create_device(device: Device):
        async with get_db() as session:
            try:
                session.add(device)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_users_devices(user_id: int) -> list[Device]:
        async with get_db() as session:
            try:
                stmt = select(Device).filter(Device.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    async def get_device_by_id(device_id: int):
        async with get_db() as session:
            try:
                device = await session.get(Device, device_id)
                if device is not None:
                    assert isinstance(device, Device)
                    return device
                raise ValueError(f"Device with id {device_id} not found")
            except SQLAlchemyError as e:
                raise e

    async def delete_device_by_id(device_id: int):
        async with get_db() as session:
            try:
                await session.delete(Device, device_id)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def update_device(self, device_id: int, device: Device):
        async with get_db() as session:
            try:
                stmt = (
                    update(Device).where(Device.device_id == device_id).values(device)
                )
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def unregister_device(self, device_id: int):
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
