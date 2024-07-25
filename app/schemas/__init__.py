from typing import Annotated
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Device
class DeviceSchema(BaseModel):
    device_id: UUID
    public_key: str
    user_id: UUID
    schedule: dict
    register_timestamp: datetime
    creation_timestamp: datetime


class ThermostatReport(BaseModel):
    temperature_celcius: float
    heater_on: bool
    timestamp: datetime


class TimeSlot(BaseModel):
    time: Annotated[str, Field(pattern=r"^\d{2}:\d{2}$")]
    temperature: Annotated[int, Field(ge=0, le=40)]

    @field_validator("time")
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format, should be HH:MM")
        return v


class DaySchedule(BaseModel):
    day: Annotated[
        str,
        Field(pattern=r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$"),
    ]
    slots: list[TimeSlot]

    @field_validator("slots")
    def check_time_conflicts(cls, slots: list[TimeSlot]):
        times = [slot.time for slot in slots]
        if len(times) != len(set(times)):
            raise ValueError("Time slots conflict within the same day")
        return slots


class ThermostatSchedule(BaseModel):
    schedule: list[DaySchedule]

    @field_validator("schedule")
    def check_schedule_conflicts(cls, schedule: list[DaySchedule]):
        for day_schedule in schedule:
            time_slots = [
                datetime.strptime(slot.time, "%H:%M") for slot in day_schedule.slots
            ]
            if len(time_slots) != len(set(time_slots)):
                raise ValueError(f"Time slots conflict within {day_schedule.day}")
        return schedule


# Device auth
class AuthRequest(BaseModel):
    device_id: UUID
    signature: str


class AuthChallenge(BaseModel):
    challenge: str
    device_id: UUID


# JWT
class Token(BaseModel):
    access_token: str
    token_type: str


class UserToken(BaseModel):
    user_id: UUID


class DeviceToken(BaseModel):
    device_id: UUID


# User
class UserSchema(BaseModel):
    user_id: UUID
    email: str
    hashed_password: str
    creation_timestamp: datetime
    is_admin: bool
