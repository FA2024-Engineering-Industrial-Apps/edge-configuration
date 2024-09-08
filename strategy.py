from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel

from factory import BikePartsFactory, CarPartsFactory, AbstractVehiclePartsFactory

from model import DeviceModel, Vehicle, VehicleTypeEnum
from llm import retrieve_model


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
