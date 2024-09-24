import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTH_URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/auth/realms/customer/protocol/openid-connect/token"


def get_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise LookupError("Client id or secret not found!")

    if "TOKEN" not in os.environ:
        response = requests.post(
            AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        if not response.ok:
            raise PermissionError(
                "No token could be generated. Please check your username and password"
            )
        os.environ["TOKEN"] = response.json()["access_token"]

    return os.environ["TOKEN"]
