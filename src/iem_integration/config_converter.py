import json
from enum import Enum

from iem_integration.devices import DetailedDevice


class AppType(Enum):
    OPC_UA_CONNECTOR = "OPC_UA_CONNECTOR"


class ConfigConverter:

    def _transform_config_for_ua_connector(self, config: dict, device: DetailedDevice) -> dict:
        with open('opc_ua_connector_config.json') as f:
            data = f.read()
        final_cfg = json.loads(data)

        config_id = "3d24e7d090bf44d8be2adaa770abd162"
        app_id = "456e041339e744caa9514a1c86536067"

        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["OPCUAUrl"] = config["urlField"]
        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["portNumber"] = config["portField"]
        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["name"] = config["nameField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["OPCUAUrl"] = config["urlField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["portNumber"] = config["portField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["name"] = config["nameField"]

        final_cfg["SystemData"]["deviceDetails"]["deviceName"] = device.name
        final_cfg["SystemData"]["deviceDetails"]["deviceId"] = device.id
        final_cfg["SystemData"]["deviceDetails"]["configId"] = config_id
        final_cfg["SystemData"]["deviceDetails"]["appId"] = app_id


        result = {
            "configId": config_id,
            "templateId": "82c6b39463d5410196b814af90ee30c4",
            "editedTemplateText": final_cfg,
        }
        return result



    def convert_to_iem_json(self, config: json,
                            device: DetailedDevice,
                            app_type: AppType) -> dict:
        if app_type == AppType.OPC_UA_CONNECTOR:
            return self._transform_config_for_ua_connector(config, device)

# cfg = UAConnectorConfig()
# cfg.nameField.value = "Franz"
# cfg.portField.value = 42080
# cfg.urlField.value = "http://localhost"
#
# conv = ConfigConverter()
# res = conv.convert_to_iem_json(cfg, AppType.OPC_UA_CONNECTOR)
# print(res)