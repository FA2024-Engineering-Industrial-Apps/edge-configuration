import requests
from constants import IEM_API
from auth import get_token


def install_app_on_edge_device(
    device_id: str, app_id: str, config: list[dict] | None = None
) -> str:
    """Installs app on edge device with optional configuration

    Args:
        device_id (str): ID of Edge device the app should be installed on
        app_id (str): ID of App that should be installed
        config (list[dict] | None, optional): Configurations of App as a dict. Defaults to None, which installs the app without configuration.

    Returns:
        str: jobId on IEM
    """    

    infoMap = {"devices": [device_id] }

    if config:
        infoMap["configs"] = config
    print(infoMap)
    response = requests.post(
        IEM_API + f"/batches",
        params={"appid": app_id, "operation": "installApplication"},
        files={"infoMap": (None, str(infoMap))},
        headers={"Authorization": get_token()},
    )

    if not response.ok:
        raise ConnectionError(
            f"App installation failed for device {device_id} \n {response.text}"
        )
    
    return response.json()["data"]


