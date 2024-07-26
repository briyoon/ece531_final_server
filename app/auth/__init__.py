from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
import os
import base64

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from schemas import UserToken, DeviceToken, AuthRequest
from models import User, Device, Challenge
from repositories import UserRepository, DeviceRepository, ChallengeRepository

load_dotenv()
JWT_SECRET = str(os.getenv("JWT_SECRET"))
JWT_ALGORITHM = str(os.getenv("JWT_ALGO"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/user/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str):
    user: User = await UserRepository.get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def authenticate_device(auth_request: AuthRequest):
    try:
        device: Device = await DeviceRepository.get_device_by_id(auth_request.device_id)
    except ValueError as e:
        raise e

    challenge_info: Challenge = await ChallengeRepository.get_challenge(
        auth_request.device_id
    )
    if not challenge_info or challenge_info.expires_at < datetime.now():
        raise ValueError("Challenge not found or expired")

    challenge = challenge_info.challenge
    public_key = serialization.load_pem_public_key(device.public_key.encode())
    signature = base64.b64decode(auth_request.signature)

    try:
        public_key.verify(
            signature,
            challenge.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
    except InvalidSignature:
        raise ValueError("Invalid signature")

    await ChallengeRepository.delete_challenge(auth_request.device_id)
    return device


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_user_from_token(token: Annotated[str, Depends(oauth2scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: UUID | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = UserToken(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    user = await UserRepository.get_user_by_id(token_data.user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_device_from_token(token: Annotated[str, Depends(oauth2scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        device_id: UUID | None = payload.get("sub")
        if device_id is None:
            raise credentials_exception
        token_data = DeviceToken(device_id=device_id)
    except InvalidTokenError:
        raise credentials_exception

    device = await DeviceRepository.get_device_by_id(token_data.device_id)

    if device is None:
        raise credentials_exception

    return device


async def get_admin_user(user: User = Depends(get_user_from_token)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="User is not an admin")
    return user
