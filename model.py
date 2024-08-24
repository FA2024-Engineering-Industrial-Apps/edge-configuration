from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Wheels(BaseModel):
    count: int
    size: float
    color: str

class Motor(BaseModel):
    power: int
    type: str

class VehicleTypeEnum(str, Enum):
    car = 'car'
    bike = 'bike'

class Vehicle(BaseModel):
    type: VehicleTypeEnum
    wheels: Wheels
    motor: Optional[Motor] = None