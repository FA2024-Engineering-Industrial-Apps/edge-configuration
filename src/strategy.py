from __future__ import annotations
from abc import ABC, abstractmethod

from llm import retrieve_model
from iem_model import App, UAConnectorConfig, AbstractAppConfig
from data_extraction import DataExtractor
from llm_service import GPT4o, GPT4Turbo
from nl_service import NLService
from typing import Tuple


class Strategy(ABC):

    @abstractmethod
    def send_message(self, prompt: str, history: list) -> Tuple[str, AbstractAppConfig]:
        pass


class EdgeConfigStrategy(Strategy):
    system_prompt = """
    You are an expert for configuring Siemens IEM.
There are many different kinds of customers, some more experienced, but also beginners, which do not how to
configure the IEM.
The Siemens IEM eco system consists of different apps, which each have to be configured.
Down below you find a list of all available apps in the IEM eco system.
Do not use any other information about IEM you have except for the app list below.
Each app consists of an "Appname", an "App-Description", which describes what the app does,
and a config.
Each config consists of fields, which have to be filled.
Each field has a name, how the field is called in the user interface, and a description, what should be entered
in this field.

{0}

You help the user to configure any app he wants to use.
For this every field of every app config he wants to use has to be filled with a value.
Ask the user for the values, and answer his questions about the apps and the fields.
    """

    def create_app_overview(self) -> str:
        opc_ua_connector = App(
            name="OPC UA Connector",
            description="A app which connects to a configured OPC UA Server and collects data from this.",
            config=UAConnectorConfig(),
        )
        return """
        {{
            apps: [
                {0}
            ]
        }}
        """.format(
            opc_ua_connector.generate_prompt_string()
        )

    def __init__(self):
        adapted_system_prompt = self.system_prompt.format(self.create_app_overview())
        self.config_object = UAConnectorConfig()
        self.nl_service = NLService(
            self.config_object, GPT4Turbo(adapted_system_prompt)
        )
        self.data_extractor = DataExtractor(self.config_object, llm=GPT4Turbo())

    def send_message(self, prompt: str, history: list) -> Tuple[str, AbstractAppConfig]:
        # print(history)
        nl_response = self.nl_service.retrieve_model(
            prompt, self.config_object, history
        )
        updated_history = history + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": nl_response},
        ]
        self.data_extractor.update_data(history + [{"role": "user", "content": prompt}])
        return nl_response, self.config_object
