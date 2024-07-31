import time
import random
from datetime import datetime
import httpx
import base64
import tomli
import tomli_w
from uuid import uuid4
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class ThermostatReport(BaseModel):
    temperature_celcius: float
    heater_on: bool
    timestamp: datetime


# Function to generate RSA key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


# Function to save key pair to PEM files
def save_key_pair_to_pem(private_key: RSAPrivateKey, pem_file_path):
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(pem_file_path, "wb") as pem_file:
        pem_file.write(private_pem)


def save_public_key_to_pub(public_key: RSAPublicKey, pub_file_path):
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(pub_file_path, "wb") as pub_file:
        pub_file.write(base64.b64encode(public_pem))


# Test routes
async def test_routes(base_url: str, device_id: str, private_key: RSAPrivateKey):
    async with httpx.AsyncClient() as client:
        # Step 1: Get challenge
        response = await client.get(f"{base_url}/auth/device/challenge/{device_id}")
        response.raise_for_status()
        challenge_data = response.json()
        challenge: str = challenge_data["challenge"]

        # Step 2: Sign challenge
        signature = private_key.sign(
            challenge.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        signature_b64 = base64.b64encode(signature).decode()

        # Step 3: Device login
        auth_request = {
            "device_id": str(device_id),
            "signature": signature_b64,
        }
        response = await client.post(f"{base_url}/auth/device/login", json=auth_request)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data["access_token"]

        print("Access Token:")
        print(access_token)

        # Step 4: Get schedule
        auth_header = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(f"{base_url}/device/schedule", headers=auth_header)
        if response.status_code == 200:
            print("Device schedule:", response.json())
        else:
            print(
                f"Failed to get device schedule: {response.status_code}, {response.text}"
            )

        # Step 5: Create 10 reports
        for _ in range(10):
            temperature = random.randint(20, 30)  # Random temperature between 20 and 30
            report_data = ThermostatReport(
                temperature_celcius=temperature,
                heater_on=True,
                timestamp=datetime.now(),
            )
            print(report_data.model_dump_json())
            # exit()
            response = await client.post(
                f"{base_url}/device/report",
                json=jsonable_encoder(report_data),
                headers=auth_header,
            )
            if response.status_code == 200:
                print("Report created successfully.")
            else:
                print(
                    f"Failed to create report: {response.status_code}, {response.text}"
                )
            time.sleep(1)


if __name__ == "__main__":
    import asyncio

    # Read configuration from config.toml
    config_path = "tests/config.toml"

    with open(config_path, "rb") as f:
        config = tomli.load(f)

    device_id = config["device"]["device_id"]
    pem_path = config["device"]["pem_path"]
    base_url = config["server"]["base_url"]

    # Check if device_id or pem_path is empty
    if not device_id or not pem_path:
        if not device_id:
            device_id = str(uuid4())
            config["device"]["device_id"] = device_id

        if not pem_path:
            pem_path = "private_key.pem"
            pub_path = "public_key.pub"
            private_key, public_key = generate_key_pair()
            save_key_pair_to_pem(private_key, pem_path)
            save_public_key_to_pub(public_key, pub_path)
            config["device"]["pem_path"] = pem_path

        # Save the updated configuration to the toml file
        with open(config_path, "wb") as f:
            tomli_w.dump(config, f)

        print(
            "Generated new device_id and/or pem_path. Please check the updated config.toml."
        )
        exit()

    # Load private key from PEM file
    with open(pem_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    asyncio.run(test_routes(base_url, device_id, private_key))
