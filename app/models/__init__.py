from datetime import datetime
import uuid

from sqlalchemy import ForeignKey, String, DateTime, UUID, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)


class Device(Base):
    __tablename__ = "device"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.user_id"))


class Report(Base):
    __tablename__ = "report"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("device.device_id"))
    temperature_celcius: Mapped[float] = mapped_column(float, nullable=False)
    heater_on: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
