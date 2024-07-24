from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from database import get_db
from models import User


class UserRepository:
    """Stateless collection of DB access functions for User model"""

    async def create_user(user: User):
        async with get_db() as session:
            try:
                session.add(user)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_user_by_email(email: str):
        async with get_db() as session:
            try:
                user = await session.get(User, email)
                if user is None:
                    raise ValueError(f"User with email {email} not found")
                return user
            except SQLAlchemyError as e:
                raise e

    async def get_user_by_id(user_id: int) -> User:
        async with get_db() as session:
            try:
                user = await session.get(User, user_id)
                if user is not None:
                    return user
                raise ValueError(f"User with id {user_id} not found")
            except SQLAlchemyError as e:
                raise e

    async def get_all_users() -> list[User]:
        async with get_db() as session:
            try:
                stmt = select(User)
                result = await session.execute(stmt)
                return result.scalars().all()
            except SQLAlchemyError as e:
                raise e

    async def delete_user_by_id(user_id: int):
        async with get_db() as session:
            try:
                await session.delete(User, user_id)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    # async def update_user(self, user_id: int, user: User):
    #     async with get_db() as session:
    #         stmt = select(User).filter(User.user_id == user_id)
    #         await session.execute(stmt)
    #         await session.commit()
