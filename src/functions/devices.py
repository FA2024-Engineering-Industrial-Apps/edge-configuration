import requests
from auth import get_token

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/p.service/api/v4"

def get_edge_devices() -> list[dict]:
    response = requests.get(URL + "/devices", headers={"Authorization": get_token()})
    return response.json()["data"]

def get_edge_device_details(device_id: str):
    print(URL + f"/devices/{device_id}")
    
    response = requests.get(URL + f"/devices/{device_id}", headers={"Authorization": get_token()})
    return response.json()


device = get_edge_devices()[0]

print(get_edge_device_details(device_id=device["deviceId"]))