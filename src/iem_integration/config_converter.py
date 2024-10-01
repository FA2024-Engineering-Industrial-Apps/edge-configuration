import json
from enum import Enum

from iem_integration.devices import DetailedDevice


class AppType(Enum):
    OPC_UA_CONNECTOR = "OPC_UA_CONNECTOR"
    DATABUS = "DATABUS"


class ConfigConverter:

    def __init__(self, config_path="src/iem_integration/configs"):
        self.config_path = config_path

    def _transform_config_for_ua_connector(self, config: dict, device: DetailedDevice) -> dict:
        with open(self.config_path + '/opc_ua_connector/OPCConf.json') as f:
            data = f.read()
        final_cfg = json.loads(data)

        config_id = "3d24e7d090bf44d8be2adaa770abd162"
        app_id = "456e041339e744caa9514a1c86536067"

        datapoint_template_uiconfig = {
            "name": "testPLC",
            "tags": [
                {
                    "name": "test",
                    "address": "web.de",
                    "dataType": "Bool",
                    "connectionType": "OPCUA",
                    "acquisitionCycle": 1000,
                    "acquisitionMode": "CyclicOnChange",
                    "accessMode": "r",
                    "comments": "Leanders testtag",
                    "operationType": "Full",
                    "deployedState": 1,
                    "isDeployed": True,
                    "id": 101,
                    "isSelected": True,
                    "hidden": False
                }
            ],
            "isSelected": True,
            "operationType": "Full",
            "isDeployed": True,
            "deployedState": 1,
            "id": 100,
            "isBrowse": False,
            "OPCUAUrl": "opc.tcp://192.123.234.134",
            "portNumber": 48010,
            "userID": "edge",
            "password": "U2FsdGVkX1//lvGIpifL1CaBhBazlOD7Rega4TlT/a0=",
            "authenticationMode": 2,
            "encryptionMode": 1,
            "securityPolicy": 1,
            "connState": "Good",
            "hidden": False
        }

        datapoint_template_configdata = {
            "name": "testPLC",
            "tags": [
                {
                    "name": "test",
                    "address": "web.de",
                    "dataType": "Bool",
                    "acquisitionCycle": 1000,
                    "acquisitionMode": "CyclicOnChange",
                    "accessMode": "r",
                    "comments": "Leanders testtag",
                    "id": 101
                }
            ],
            "operationType": "Full",
            "id": 100,
            "isBrowse": False,
            "OPCUAUrl": "opc.tcp://192.123.234.134",
            "portNumber": 48010,
            "userID": "edge",
            "password": "U2FsdGVkX1//lvGIpifL1CaBhBazlOD7Rega4TlT/a0=",
            "authenticationMode": 2,
            "encryptionMode": 1,
            "securityPolicy": 1,
            "connState": "No State"
        }

        for i in range(len(config["datapoints"])):
            final_cfg["UIConfig"]["datapoints"]["OPCUA"].append(datapoint_template_uiconfig)
            final_cfg["ConfigData"]["datapoints"]["OPCUA"].append(datapoint_template_configdata)
            name = config["datapoints"][i]["name"]
            tag_name = config["datapoints"][i]["tags"][0]["name"]
            tag_address = config["datapoints"][i]["tags"][0]["address"]
            tag_dataType = config["datapoints"][i]["tags"][0]["dataType"]
            tag_acquisition_cycle = config["datapoints"][i]["tags"][0]["acquisitionCycle"]
            tag_acquisition_mode = config["datapoints"][i]["tags"][0]["acquisitionMode"]
            tag_isArrayTypeTag = config["datapoints"][i]["tags"][0]["isArrayTypeTag"]
            tag_accessMode = config["datapoints"][i]["tags"][0]["accessMode"]
            tag_comments = config["datapoints"][i]["tags"][0]["comments"]
            OPCUAUrl = config["datapoints"][i]["OPCUAUrl"]
            portNumber = config["datapoints"][i]["portNumber"]
            authenticationMode = config["datapoints"][i]["authenticationMode"]
            if name:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["name"] = name
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["name"] = name
            if tag_name:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["name"] = tag_name
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["name"] = tag_name
            if tag_address:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["address"] = tag_address
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["address"] = tag_address
            if tag_dataType:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["dataType"] = tag_dataType
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["dataType"] = tag_dataType
            if tag_acquisition_cycle:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["acquisitionCycle"] = tag_acquisition_cycle
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["acquisitionCycle"] = tag_acquisition_cycle
            if tag_acquisition_mode:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["acquisitionMode"] = tag_acquisition_mode
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["acquisitionMode"] = tag_acquisition_mode
            if tag_accessMode:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["accessMode"] = tag_accessMode
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["accessMode"] = tag_accessMode
            if tag_comments:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["tags"][0]["comments"] = tag_comments
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["tags"][0]["comments"] = tag_comments
            if OPCUAUrl:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["OPCUAUrl"] = OPCUAUrl
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["OPCUAUrl"] = OPCUAUrl
            if portNumber:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["portNumber"] = portNumber
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["portNumber"] = portNumber
            if authenticationMode:
                final_cfg["UIConfig"]["datapoints"]["OPCUA"][i]["authenticationMode"] = authenticationMode
                final_cfg["ConfigData"]["datapoints"]["OPCUA"][i]["authenticationMode"] = authenticationMode
        dbservicename = config["dbservicename"]
        username = config["username"]
        password = config["password"]
        if dbservicename:
            final_cfg["UIConfig"]["dbservicename"] = dbservicename
        if username:
            final_cfg["UIConfig"]["username"] = username
        if password:
            final_cfg["UIConfig"]["password"] = password

        final_cfg["SystemData"]["deviceDetails"]["deviceName"] = device.name
        final_cfg["SystemData"]["deviceDetails"]["deviceId"] = device.id
        final_cfg["SystemData"]["deviceDetails"]["configId"] = config_id
        final_cfg["SystemData"]["deviceDetails"]["appId"] = app_id

        result = {
            "configId": config_id,
            "templateId": "82c6b39463d5410196b814af90ee30c4",
            "editedTemplateText": json.dumps(final_cfg),
        }
        return result

    def convert_to_iem_json(self, config: json,
                            device: DetailedDevice,
                            app_type: AppType) -> dict:
        if app_type == AppType.OPC_UA_CONNECTOR:
            return self._transform_config_for_ua_connector(config, device)

# cfg = DocumentationUAConnectorConfig()
# cfg.nameField.value = "Franz"
# cfg.portField.value = 42080
# cfg.urlField.value = "http://localhost"
#
#conv = ConfigConverter()
#res = conv.convert_to_iem_json(cfg, AppType.OPC_UA_CONNECTOR)
#print(res)
# print(cfg.to_json())
