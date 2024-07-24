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
    creation_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )


class Device(Base):
    __tablename__ = "device"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    public_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.user_id"), nullable=True
    )  # if device is not registered, user_id is None
    register_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    creation_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )


class Report(Base):
    __tablename__ = "report"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.user_id"))
    device_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("device.device_id"))
    temperature_celcius: Mapped[float] = mapped_column(float, nullable=False)
    heater_on: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Challenge(Base):
    __tablename__ = "challenge"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("device.device_id"), primary_key=True
    )
    challenge: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
