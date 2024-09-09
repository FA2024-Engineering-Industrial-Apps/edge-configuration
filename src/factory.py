from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel
from model import Motor, Wheels, VehicleTypeEnum, Vehicle
from typing import Optional
from llm import retrieve_model


class AbstractVehiclePartsFactory(ABC):

    @abstractmethod
    def create_wheels(self, description: str) -> Wheels:
        pass

    @abstractmethod
    def create_motor(self, description: str) -> Optional[Motor]:
        pass


class BikePartsFactory(AbstractVehiclePartsFactory):

    def create_wheels(self, description: str) -> Wheels:
        return retrieve_model(
            description,
            Wheels,
            "You're part of a vehicle factory and returning the configuration parts for a vehicle.",
        )

    def create_motor(self, description: str) -> Optional[Motor]:
        return None


class CarPartsFactory(AbstractVehiclePartsFactory):

    def create_wheels(self, description: str) -> Wheels:
        return retrieve_model(
            description,
            Wheels,
            "You're part of a vehicle factory and returning the configuration parts for a vehicle.",
        )

    def create_motor(self, description: str) -> Optional[Motor]:
        return retrieve_model(
            description,
            Motor,
            "You're part of a vehicle factory and returning the configuration parts for a vehicle.",
        )
