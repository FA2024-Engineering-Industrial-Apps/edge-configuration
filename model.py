from pydantic import BaseModel
from typing import Optional
from enum import Enum
from pydantic import Field


class Wheels(BaseModel):
    count: int
    size: float
    color: str


class Motor(BaseModel):
    power: int
    type: str


class VehicleTypeEnum(str, Enum):
    car = "car"
    bike = "bike"


class Vehicle(BaseModel):
    type: VehicleTypeEnum
    wheels: Wheels
    motor: Optional[Motor] = None


class Device(BaseModel):
    edge_device_type: str = Field(
        description="Device type of the Edge Device you want to onboard, for example SIMATIC IPC227E"
    )
    edge_device_name: str = Field(
        description="""
            Unique domain wide name of the Edge Device
            Must contain 3 - 64 characters
        """
    )
    edge_device_username: str = Field(
        description="Valid email address of the user for signing into the Edge Device"
    )
    edge_device_password: str = Field(
        description="""Password for signing into the Edge Device
            Minimum 8 characters
            Minimum 1 upper case letter
            Minimum 1 special character
            Minimum 1 number
            The following characters are recognized as special characters:
            ! @ # $ % ^ & * . ( ) _ +")"""
    )
    edge_device_confirm_password: str = Field(
        description="Confirm Edge Device password"
    )


class NetworkInterface(BaseModel):
    gateway_interface: str
    mac_address: str
    ethernet_label: str
    dhcp: str
    ipv4: str
    netmask: str
    gateway: str
    primary_dns: str
    secondary_dns: str
    start_ip_address: str
    netmask_2: str
    ip_address_range: str


class Proxy(BaseModel):
    host: str
    protocol: str
    user: str
    password: str
    no_proxy: Optional[str]
    custom_ports: str


class EdgeDevice(BaseModel):
    device: Device
    network_interface: NetworkInterface
    proxy: Proxy
