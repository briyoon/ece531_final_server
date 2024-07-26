import threading
import contextlib
import os
from dotenv import load_dotenv
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert

from models import Base, User

SessionLocal: sessionmaker | None = None
_lock = threading.Lock()


async def init_models():
    load_dotenv()
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")

    engine = create_async_engine(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
        echo=True,
    )
    global SessionLocal
    SessionLocal = sessionmaker(
        expire_on_commit=False, class_=AsyncSession, bind=engine
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # init admin user
        # try:
        #     await conn.execute(
        #         User.__table__.select().where(
        #             User.user_id == "648913b6-6a50-463d-ac58-127069201330"
        #         )
        #     )
        # except:
        #     await conn.execute(
        #         insert(User).values(
        #             user_id=UUID("648913b6-6a50-463d-ac58-127069201330"),
        #             email="admin@gmail.com",
        #             hashed_password="$2b$12$7EXTGKlQZsO3oaCa46N3Ve5EPl75HQhPGdslibPu8vktCSzDi4hwK",
        #             is_admin=True,
        #         )
        #     )


@contextlib.asynccontextmanager
async def get_db():
    global SessionLocal
    if SessionLocal is None:
        with _lock:
            if SessionLocal is None:
                try:
                    await init_models()
                except Exception as e:
                    raise RuntimeError("Failed to initialize database session.") from e

    db: AsyncSession = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
