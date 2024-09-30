from __future__ import annotations

# from builtins import classmethod
from typing import List, Optional
from iem_integration.install_app import install_app_on_edge_device
from iem_integration.config_converter import ConfigConverter, AppType
from iem_integration.constants import OPC_UA_CONNECTOR_APP_ID
from iem_integration.devices import get_device_details

from model.iem_base_model import *
from model.iem_model import *


# class containing all data of an app including its Config
class App:
    application_name: str
    app_id: str
    application_description: str
    installed_device_name: Optional[str] = None
    config: AbstractAppConfig

    def __init__(self, name: str, id: str, description: str, config: AbstractAppConfig):
        self.application_name = name
        self.application_description = description
        self.config = config
        self.app_id = id

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
                "description": f"Install the app {self.application_name} to the IEM.",
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

        set_device_name_fct_data = FunctionDescriptionPair(
            name=self.application_name + "-set_device_name",
            fct=self.set_device_name,
            llm_description=set_device_name_fct,
        )

        return [
            submit_fct,
            set_device_name_fct_data,
        ] + self.config.generate_tool_functions()

    def generate_prompt_sidebar(self) -> str:
        result = f"""
        App-Name: {self.application_name}
        Device Name: {self.installed_device_name}
        Config: {self.config.generate_prompt_sidebar()}
        """
        return result

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
        for app in self.apps:
            result_list += app.generate_tool_functions()
        # print("TOOL FUNCTIONS: ")
        # print(result_list)
        return result_list

    def generate_prompt_sidebar(self) -> str:
        result = ""
        for app in self.apps:
            result += app.generate_prompt_sidebar()
            result += "-----------------------------\n"
        return result
