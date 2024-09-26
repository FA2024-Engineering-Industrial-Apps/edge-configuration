import requests

from pydantic import BaseModel
from constants import IEM_API, PORTAL_SERVICE_API
from auth import get_token


class Device(BaseModel):
    name: str
    id: str
    status: str
    url: str


def get_device_details(device_name: str) -> Device:
    """Provides details on Industrial edge device

    Args:
        device_name (str): device name as defined in IEM

    Returns:
        Device: Device details
    """
    device_response = requests.get(
        IEM_API + "/devices", headers={"Authorization": get_token()}
    )
    if not device_response.ok:
        raise ConnectionError(
            f"Error when trying to get device list \n {device_response.text}"
        )

    device_list = device_response.json()["data"]

    for device in device_list:
        if device["deviceName"] == device_name:
            my_device = device
            break

    if not my_device:
        raise LookupError(f"No device with name {device_name} found")

    device_id = my_device["deviceId"]
    print(device_id)
    device_details_response = requests.get(
        PORTAL_SERVICE_API + f"/devices/{device_id}",
        headers={"Authorization": get_token()},
    )

    if not device_details_response.ok:
        raise ConnectionError(
            f"Error when trying to get device details for device with id {device_id} \n {device_details_response.text}"
        )

    device_details = device_details_response.json()["data"][0]

    return Device(
        name=device_name,
        id=device_id,
        status=device_details["deviceStatus"],
        url=device_details["nodes"][0]["discoveryDetailsVO"]["sLocalIPAddress"],
    )
