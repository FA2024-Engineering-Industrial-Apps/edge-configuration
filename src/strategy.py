from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from llm import retrieve_model
from iem_model import App, UAConnectorConfig, AbstractAppConfig, AppModel
from data_extraction import DataExtractor
from llm_service import GPT4o, GPT4Turbo
from nl_service import NLService
from typing import Tuple
from history import History


class Strategy(ABC):
    def __init__(self):
        self.history = History()

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
an "installed_device_name", which is the device name in IEM, where the app should be installed,
and a config.
Each config consists of fields, which have to be filled.
Each field has a name, how the field is called in the user interface, and a description, what should be entered
in this field.

{0}

You help the user to configure any app he wants to use.
For this every field of every app config he wants to use has to be filled with a value.
Before the user can install the apps to the IEM, for every app the "installed_device_name" has to be set.
Ask the user for the values, and answer his questions about the apps and the fields.
Only after all fields and the "installed_device_name" is set an app may be installed to IEM.

If there is nonsensical information for setting one of the values, skip this value but continue with the next one and call the setter function.
    """

    opc_ua_connector = App(
        name="OPC_UA_CONNECTOR",
        description="A app which connects to a configured OPC UA Server and collects data from this.",
        config=UAConnectorConfig(),
        id="456e041339e744caa9514a1c86536067"
    )

    def create_app_overview(self) -> str:
        return """
        {{
            apps: [
                {0}
            ]
        }}
        """.format(
            self.opc_ua_connector.generate_prompt_string()
        )

    def __init__(self):
        super().__init__()
        adapted_system_prompt = self.system_prompt.format(
            self.create_app_overview()
        )
        self.model: AppModel = AppModel()
        self.model.apps = [self.opc_ua_connector]
        self.nl_service = NLService(self.model,
                                    GPT4o(adapted_system_prompt))
        self.data_extractor = DataExtractor(self.model)

        self.history.addSystemPromt(adapted_system_prompt)

        # add first entry to the configHistory
        self.history.addConfig(self.model)

    def send_message(self):

        self.data_extractor.update_data(self.history)   # changes model, adds new model to configHistory and adds validation promts to promtHistory if necessary

        self.nl_service.retrieve_model(self.history)    # adds assistent response to history
        
