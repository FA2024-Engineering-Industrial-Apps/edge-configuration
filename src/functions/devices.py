import requests
import json

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"

user_name = ""
password = ""


def get_token() -> str:
    response = requests.post(
        URL + "/login/direct", json={"username": user_name, "password": password}
    )
    token = response.json()["data"]["access_token"]

    return token


def get_edge_devices() -> list[dict]:
    response = requests.get(URL + "/devices", headers={"Authorization": get_token()})
    return response.json()["data"]

print(get_edge_devices())
