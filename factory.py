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
        return retrieve_model(description, Wheels)

    def create_motor(self, description: str) -> Optional[Motor]:
        return None
    
class CarPartsFactory(AbstractVehiclePartsFactory):

    def create_wheels(self, description: str) -> Wheels:
        return retrieve_model(description, Wheels)

    def create_motor(self, description: str) -> Optional[Motor]:
        return retrieve_model(description, Motor)
    

def llm_determine_vehicle_type(description: str) -> VehicleTypeEnum:
    return retrieve_model(description, VehicleTypeEnum)

def get_factory(vehicle_type: VehicleTypeEnum) -> AbstractVehiclePartsFactory:
    if vehicle_type == 'bike':
        return BikePartsFactory()
    elif vehicle_type == 'car':
        return CarPartsFactory()
    else:
        raise ValueError(f'Unknown vehicle type: {vehicle_type}')
    
def create_vehicle(description: str) -> Vehicle:
    vehicle_type = llm_determine_vehicle_type(description)
    factory = get_factory(vehicle_type)
    wheels = factory.create_wheels(description)
    motor = factory.create_motor(description)
    return Vehicle(type=vehicle_type, wheels=wheels, motor=motor)