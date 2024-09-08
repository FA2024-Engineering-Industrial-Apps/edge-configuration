from pydantic import BaseModel, Field
from typing import List, Optional
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


class StaticConfig(BaseModel):
    IPv4: Optional[str] = ""
    NetMask: Optional[str] = ""
    Gateway: Optional[str] = ""


class DNSConfig(BaseModel):
    PrimaryDNS: str
    SecondaryDNS: str


class L2Conf(BaseModel):
    StartingAddressIPv4: str
    NetMask: str
    Range: str


class SelectedL2Range(BaseModel):
    id: str
    nameToString: str


class Interface(BaseModel):
    MacAddress: str
    GatewayInterface: bool
    DHCP: str
    Static: StaticConfig
    DNSConfig: DNSConfig
    L2Conf: L2Conf
    isL2NetworkDisable: bool
    selectedL2Range: SelectedL2Range


class Network(BaseModel):
    Interfaces: List[Interface]


class DeviceConfig(BaseModel):
    Network: Network
    dockerIP: str


class Onboarding(BaseModel):
    localUserName: str
    localPassword: str
    deviceName: str


class NTPServer(BaseModel):
    ntpServer: str
    preferred: Optional[bool] = False


class Proxy(BaseModel):
    host: str
    protocol: str
    user: str
    password: str


class Device(BaseModel):
    onboarding: Onboarding
    Device: DeviceConfig
    ntpServers: List[NTPServer]
    proxies: List[Proxy]


class DeviceModel(BaseModel):
    device: Device
