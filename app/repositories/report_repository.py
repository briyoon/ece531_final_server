from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from database import get_db
from models import Report


class ReportRepository:
    """Stateless collection of DB access functions for Report model"""

    @staticmethod
    async def create_report(report: Report):
        async with get_db() as session:
            try:
                session.add(report)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @staticmethod
    async def get_user_reports(user_id: UUID) -> list[Report]:
        async with get_db() as session:
            try:
                stmt = select(Report).filter(Report.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    @staticmethod
    async def get_user_device_reports_after_time(
        user_id: UUID, device_id: UUID, after_time: datetime
    ) -> list[Report]:
        async with get_db() as session:
            try:
                stmt = select(Report).filter(
                    Report.user_id == user_id,
                    Report.device_id == device_id,
                    Report.timestamp > after_time,
                )
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    @staticmethod
    async def get_device_reports(device_id: UUID) -> list[Report]:
        async with get_db() as session:
            try:
                stmt = select(Report).filter(Report.device_id == device_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e
