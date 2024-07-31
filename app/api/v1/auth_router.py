from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4
from dotenv import load_dotenv
import os

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from models import Device, Challenge
from schemas import Token, AuthChallenge, AuthRequest
from repositories import DeviceRepository, ChallengeRepository
from auth import authenticate_user, authenticate_device, create_access_token

load_dotenv("")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_LENGTH_MINUTES"))

auth_router = APIRouter()


@auth_router.post("/user/login")
async def user_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/device/login")
async def device_login(auth_request: AuthRequest):
    try:
        device = await authenticate_device(auth_request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(device.device_id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/device/challenge/{device_id}")
async def get_challenge(device_id: UUID):
    device: Device = await DeviceRepository.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    challenge_info: Challenge = await ChallengeRepository.get_challenge(device_id)
    if challenge_info:
        if challenge_info.expires_at > datetime.now():
            return AuthChallenge(
                challenge=challenge_info.challenge, device_id=device_id
            )
        else:
            await ChallengeRepository.delete_challenge(device_id)

    challenge = uuid4().hex
    expires_at = datetime.now() + timedelta(minutes=5)
    await ChallengeRepository.create_challenge(device_id, challenge, expires_at)

    return AuthChallenge(challenge=challenge, device_id=device_id)
