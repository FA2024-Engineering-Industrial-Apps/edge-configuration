from apps import install_app_on_edge_device
from auth import get_token
import requests
import json

URL = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud/portal/api/v1"


ROMABRUEGGE_ID = "2672ceefded041948d82820056d1de0e"
OPC_UA_CONNECTOR_ID = "456e041339e744caa9514a1c86536067"


def create_configured_app():

    
    #install_app_on_edge_device(OPC_UA_CONNECTOR_ID, ROMABRUEGGE_ID)

    with open("../json/example4.json", "r") as f:
        infoMap = {"infoMap": (
                    None,
                    str(
                        {
                            "devices": [ROMABRUEGGE_ID],
                            "configs": [
                                {
                                    "configId": "3d24e7d090bf44d8be2adaa770abd162",
                                    "templateId": "82c6b39463d5410196b814af90ee30c4",
                                    "editedTemplateText": f.read()
                                }
                            ],
                        }
                    ),
                )}
        
        print(infoMap)
        
        
        response = requests.post(
            URL + f"/batches",
            params={"appid": OPC_UA_CONNECTOR_ID, "operation": "updateAppConfig"},
            files=infoMap,
            headers={"Authorization": get_token()},
        )

        print(response)
        


create_configured_app()
