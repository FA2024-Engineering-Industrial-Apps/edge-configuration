import requests
from auth import get_token

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"

def get_edge_devices() -> list[dict]:
    response = requests.get(URL + "/devices", headers={"Authorization": get_token()})
    return response.json()["data"]


