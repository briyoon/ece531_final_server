from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete

from models import Challenge
from database import get_db


class ChallengeRepository:
    """Stateless collection of DB access functions for Challenge model"""

    async def create_challenge(device_id: UUID, challenge: str, expires_at: datetime):
        async with get_db() as session:
            try:
                new_challenge = Challenge(
                    device_id=device_id, challenge=challenge, expires_at=expires_at
                )
                session.add(new_challenge)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_challenge(device_id: UUID) -> Challenge:
        async with get_db() as session:
            try:
                stmt = select(Challenge).filter(Challenge.device_id == device_id)
                result = await session.execute(stmt)
                return result.scalars().first()
            except SQLAlchemyError as e:
                raise e

    async def delete_challenge(device_id: UUID):
        async with get_db() as session:
            try:
                stmt = delete(Challenge).where(Challenge.device_id == device_id)
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
