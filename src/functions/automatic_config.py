from apps import install_app_on_edge_device
from auth import get_token
import requests

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"


ROMABRUEGGE_ID = "2672ceefded041948d82820056d1de0e"
OPC_UA_CONNECTOR_ID = "456e041339e744caa9514a1c86536067"


def create_configured_app():

    install_app_on_edge_device(OPC_UA_CONNECTOR_ID, ROMABRUEGGE_ID)
    return
    with open("./example2.json", "rb") as f:
        response = requests.post(
            URL + f"/batches",
            params={"appid": OPC_UA_CONNECTOR_ID, "operation": "updateApplication"},
            files={"infoMap": (None, str({"devices": [ROMABRUEGGE_ID]})), "file": f},
            headers={"Authorization": get_token()},
        )

        print(response.text)


create_configured_app()
