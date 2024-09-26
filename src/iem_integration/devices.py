import requests

from pydantic import BaseModel
from constants import IEM_API, PORTAL_SERVICE_API
from auth import get_token


class Device(BaseModel):
    name: str
    id: str
    status: str


class DetailedDevice(Device):
    url: str


def get_device_list() -> list[Device]:
    """Get list of all edge devices conncted to the IEM

    Returns:
        list[Device]: list of devices
    """
    device_response = requests.get(
        IEM_API + "/devices", headers={"Authorization": get_token()}
    )

    raw_devices = device_response.json()["data"]
    print(raw_devices)
    devices = []
    for raw_device in raw_devices:
        devices.append(
            Device(
                name=raw_device["deviceName"],
                id=raw_device["deviceId"],
                status=raw_device["deviceStatus"],
            )
        )

    return devices


def get_device_details(device_name: str) -> DetailedDevice:
    """Provides details on Industrial edge device

    Args:
        device_name (str): device name as defined in IEM

    Returns:
        DetailedDevice: Device with additional details (url)
    """

    devices = get_device_list()

    for device in devices:
        if device.name == device_name:
            my_device = device
            break

    if not my_device:
        raise LookupError(f"No device with name {device_name} found")

    device_details_response = requests.get(
        PORTAL_SERVICE_API + f"/devices/{my_device.id}",
        headers={"Authorization": get_token()},
    )

    if not device_details_response.ok:
        raise ConnectionError(
            f"Error when trying to get device details for device with id {my_device.id} \n {device_details_response.text}"
        )

    device_details = device_details_response.json()["data"][0]

    return DetailedDevice(
        name=my_device.name,
        id=my_device.id,
        status=device.status,
        url=device_details["nodes"][0]["discoveryDetailsVO"]["sLocalIPAddress"],
    )


print(get_device_list())
print(get_device_details("ipcbernius01").id)
