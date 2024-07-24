from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from database import get_db
from models import Report


class ReportRepository:
    """Stateless collection of DB access functions for Report model"""

    async def create_report(report: Report):
        async with get_db() as session:
            try:
                session.add(report)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_user_reports(user_id: int) -> list[Report]:
        async with get_db() as session:
            try:
                stmt = select(Report).filter(Report.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    async def get_device_reports(device_id: int) -> list[Report]:
        async with get_db() as session:
            try:
                stmt = select(Report).filter(Report.device_id == device_id)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e
