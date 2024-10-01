from __future__ import annotations

# from builtins import classmethod
from typing import List, Optional
from iem_integration.install_app import install_app_on_edge_device
from iem_integration.config_converter import ConfigConverter, AppType
from iem_integration.constants import OPC_UA_CONNECTOR_APP_ID
from iem_integration.devices import get_device_details

from model.iem_base_model import *
from model.iem_model import *

from model.iem_model import DocumentationUAConnectorConfig


# class containing all data of an app including its Config
# class containing all data of an app including its Config
class App:
    application_name: str
    app_id: str
    application_description: str
    installed_device_name: str = None
    config: AbstractAppConfig

    def __init__(self, name: str, id: str, description: str, config: AbstractAppConfig):
        self.application_name = name
        self.application_description = description
        self.config = config
        self.app_id = id

    def fill_from_json(self, json: Dict):
        self.application_name = json["App-name"]
        self.installed_device_name = json["Device-name"]
        self.config.fill_from_json(json)

    def generate_prompt_string(self) -> str:
        return """
        {{
            app-name: {0},
            app-description: {1},
            installed_device_name: {2}
            fields: {3}
        }}
        """.format(
            self.application_name,
            self.application_description,
            self.installed_device_name,
            self.config.generate_prompt_string(),
        )

    def generate_tool_functions(self) -> List[FunctionDescriptionPair]:
        submit_dict = {
            "type": "function",
            "function": {
                "name": self.application_name + "_submit_to_iem",
                "description": f"Install or submit the app {self.application_name} to the IEM.",
                "parameters": {},
                "required": [],
            },
        }
        submit_fct = FunctionDescriptionPair(
            name=self.application_name + "_submit_to_iem",
            fct=self.submit_to_iem,
            llm_description=submit_dict,
        )

        set_device_name_fct = {
            "type": "function",
            "function": {
                "name": self.application_name + "-set_device_name",
                "description": f"Set the installed_device_name for {self.application_name}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "val": {
                            "type": "string",
                            "description": "the new installed_device_name",
                        },
                    },
                    "required": ["installed_device_name"],
                },
            },
        }

        set_device_name_fct = FunctionDescriptionPair(
            name=self.application_name + "-set_device_name",
            fct=self.set_device_name,
            llm_description=set_device_name_fct,
        )

        return [submit_fct, set_device_name_fct] + self.config.generate_tool_functions()

    def generate_app_info(self) -> Dict:
        base_info = {
            "App-name": self.application_name,
            "Device-name": self.installed_device_name,
        }
        parameter = self.config.to_json()

        for k, v in parameter.items():
            base_info[k] = v

        return base_info

    def submit_to_iem(self):
        converter = ConfigConverter()
        device_details = get_device_details(self.installed_device_name)
        prepared_config = converter.convert_to_iem_json(
            self.config.to_json(), device_details, AppType[self.application_name]
        )
        # print("DONE")
        # print(device_details.id)
        # print(OPC_UA_CONNECTOR_APP_ID)
        # print(prepared_config)
        install_app_on_edge_device(
            device_details.id, OPC_UA_CONNECTOR_APP_ID, [prepared_config]
        )

    def set_device_name(self, val):
        self.installed_device_name = val


class AppModel:
    apps: List[App]

    def generate_prompt_string(self) -> str:
        result = "["
        for app in self.apps:
            result += app.generate_prompt_string()
        result += "]"
        return result

    def generate_tool_functions(self) -> List[FunctionDescriptionPair]:
        result_list = []
        new_app_description = {
            "type": "function",
            "function": {
                "name": "add_app",
                "description": f"Create a new app to configure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "val": {
                            "type": "string",
                            "description": f"The name of the app, which should be added. Possible options are:"
                            f"OPC_UA_CONNECTOR, DATABUS.",
                        },
                    },
                    "required": ["val"],
                },
            },
        }
        result_list.append(
            FunctionDescriptionPair(
                name="add_app",
                fct=self.add_app,
                llm_description=new_app_description,
            )
        )
        print(f"self.apps length is {len(self.apps)}")
        for app in self.apps:
            result_list += app.generate_tool_functions()
        # print("TOOL FUNCTIONS: ")
        # print(result_list)
        return result_list

    def generate_prompt_sidebar(self) -> Dict:
        result = {}
        for app in self.apps:
            dct = app.generate_app_info()
            for k, v in dct.items():
                result[k] = v
        return result

    def add_app(self, val: str):
        app_type = AppType[val]
        if app_type == AppType.OPC_UA_CONNECTOR:
            print("got here")
            new_app = App(
                name="OPC_UA_CONNECTOR",
                description="A app which connects to a configured OPC UA Server and collects data from this.",
                config=DocumentationUAConnectorConfig(),
                id="456e041339e744caa9514a1c86536067",
            )
            print("got here too")
            self.apps.append(new_app)
            print(f"now app.length = {len(self.apps)}")
