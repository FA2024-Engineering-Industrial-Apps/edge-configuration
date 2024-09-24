from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel

from factory import BikePartsFactory, CarPartsFactory, AbstractVehiclePartsFactory

from model import DeviceModel, Vehicle, VehicleTypeEnum
from llm import retrieve_model
from iem_model import App, UAConnectorConfig


class Strategy(ABC):

    @abstractmethod
    def create_product(self, prompt: str) -> BaseModel:
        pass


class VehicleStrategy(ABC):

    def llm_determine_vehicle_type(self, description: str) -> VehicleTypeEnum:
        return retrieve_model(
            description,
            VehicleTypeEnum,  # type: ignore
            "You're part of a vehicle factory and returning the configuration parts for a vehicle.",
        )  # type: ignore

    def get_factory(self, vehicle_type: VehicleTypeEnum) -> AbstractVehiclePartsFactory:
        if vehicle_type == "bike":
            return BikePartsFactory()
        elif vehicle_type == "car":
            return CarPartsFactory()
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

    def create_product(self, prompt: str) -> Vehicle:
        vehicle_type = self.llm_determine_vehicle_type(prompt)
        factory = self.get_factory(vehicle_type)
        wheels = factory.create_wheels(prompt)
        motor = factory.create_motor(prompt)
        return Vehicle(type=vehicle_type, wheels=wheels, motor=motor)


class EdgeDeviceStrategy(Strategy):

    def create_product(self, prompt: str) -> DeviceModel:
        return retrieve_model(
            prompt,
            DeviceModel,  # type: ignore
            "You're part of a edge device factory and returning the configuration parts for an edge device.",
        )  # type: ignore


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
            config=UAConnectorConfig()
        )
        return """
        {{
            apps: [
                {0}
            ]
        }}
        """.format(opc_ua_connector.generate_prompt_string())

    def create_product(self, prompt: str) -> str:
        adapted_system_prompt = self.system_prompt.format(self.create_app_overview())
        print(adapted_system_prompt)
        config_object = UAConnectorConfig()
        return retrieve_model(
            prompt,
            config_object,
            adapted_system_prompt
        )
