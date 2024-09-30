import json

from constants import CONFIG_LOCATION, OPC_UA_SERVER_APP_ID
from devices import get_device_details, get_device_list
from get_app_details import get_app_details
from install_app import install_app_on_edge_device

details = get_app_details(OPC_UA_SERVER_APP_ID)
print(details)
devices = get_device_list()
for device in devices:
    print(device.name)


device = get_device_details("Romabruegge")

config_list = []

for config in details.configs:
    print(
        f"Template {config.name} ({config.templateFileName}), id: {config.id}, template id: {config.templateId}"
    )

    with open(f"{CONFIG_LOCATION}/opc_ua_server/{config.templateFileName}", "r") as f:
        config_list.append(
            {
                "configId": config.id,
                "templateId": config.templateId,
                "editedTemplateText": f.read(),
            }
        )

# print(str(config_list))
with open("data_combined.json", "w") as f:
    json.dump(config_list, f, indent=2)

install_app_on_edge_device(device.id, OPC_UA_SERVER_APP_ID, config_list)
