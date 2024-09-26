import json
from enum import Enum

from src.iem_model import AbstractAppConfig, UAConnectorConfig


class AppType(Enum):
    OPC_UA_CONNECTOR = "OPC_UA_CONNECTOR"


class ConfigConverter:

    def _transform_config_for_ua_connector(self, config: dict) -> dict:
        with open('opc_ua_connector_config.json') as f:
            data = f.read()
        final_cfg = json.loads(data)
        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["OPCUAUrl"] = config["urlField"]
        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["portNumber"] = config["portField"]
        final_cfg["UIConfig"]["datapoints"]["OPCUA"][0]["name"] = config["nameField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["OPCUAUrl"] = config["urlField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["portNumber"] = config["portField"]
        final_cfg["ConfigData"]["datapoints"]["OPCUA"][0]["name"] = config["nameField"]

        result = {
            "configId": "3d24e7d090bf44d8be2adaa770abd162",
            "templateId": "82c6b39463d5410196b814af90ee30c4",
            "editedTemplateText": final_cfg,
        }
        return result



    def convert_to_iem_json(self, config: AbstractAppConfig,
                            app_type: AppType) -> dict:
        current_config = config.to_json()
        if app_type == AppType.OPC_UA_CONNECTOR:
            return self._transform_config_for_ua_connector(current_config)

cfg = UAConnectorConfig()
cfg.nameField.value = "Franz"
cfg.portField.value = 42080
cfg.urlField.value = "http://localhost"

conv = ConfigConverter()
res = conv.convert_to_iem_json(cfg, AppType.OPC_UA_CONNECTOR)
print(res)