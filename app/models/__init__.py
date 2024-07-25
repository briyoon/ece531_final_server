from datetime import datetime
import uuid

from sqlalchemy import Column, ForeignKey, String, DateTime, UUID, Boolean, JSON, Float
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


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
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="user")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Device(Base):
    __tablename__ = "device"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    public_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("user.user_id"), nullable=True
    )  # if device is not registered, user_id is None
    schedule: Mapped[dict] = mapped_column(JSON, nullable=True)
    register_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    creation_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    user: Mapped["User"] = relationship("User", back_populates="devices")


class Report(Base):
    __tablename__ = "report"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.user_id"))
    device_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("device.device_id"))
    temperature_celcius: Mapped[float] = mapped_column(Float, nullable=False)
    heater_on: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Challenge(Base):
    __tablename__ = "challenge"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("device.device_id"), primary_key=True
    )
    challenge: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
