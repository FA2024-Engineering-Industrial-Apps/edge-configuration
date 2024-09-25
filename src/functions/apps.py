import requests
from auth import get_token
import time
URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"


def install_app_on_edge_device(app_id: str, device_id: str):
    response = requests.post(
        URL + f"/batches",
        params={"appid": app_id, "operation": "installApplication"},
        files={"infoMap": (None, str({"devices": [device_id]}))},
        headers={"Authorization": get_token()},
    )
    if not response.ok:
        raise PermissionError(f"Can not install server on device ({response.text})")

    installed = False
    
    while not installed:
        response = requests.get(
            URL + f"/devices/installed-apps",
            headers={"Authorization": get_token()},
        )
        for app in response.json()["data"]:
            if app["deviceId"] == device_id and app["applicationId"] == app_id:
                return app
        time.sleep(1)