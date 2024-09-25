import requests
from auth import get_token
import json

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"

def get_applications():
    response = requests.get(
        URL + "/applications", headers={"Authorization": get_token()}
    )
    return response.json()["data"]


def get_application_configuration(app_id: str):
    url =  URL + f"/applications/{app_id}/configs"
    print(url)
    response = requests.get(
        URL + f"/applications/{app_id}/configs", headers={"Authorization": get_token()}
    )
    return response.json()["data"]


def get_application_configuration_template(
    app_id: str, config_id: str, template_id: str
):
    url = URL + f"/applications/{app_id}/configs/{config_id}/template/{template_id}"
    print(url)
    response = requests.get(
        url,
        headers={"Authorization": get_token()},
    )
    return response.text

print(get_application_configuration("456e041339e744caa9514a1c86536067"))