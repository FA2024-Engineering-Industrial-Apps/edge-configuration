from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict


class Field(ABC, BaseModel):
    name: str
    description: str

    @abstractmethod
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        pass


class NestedField(Field, ABC):

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_type in self.__dict__.items():
            field_value = getattr(self, field_name)
            if isinstance(field_value, Field):
                if hasattr(field_value, "generate_tool_functions") and callable(
                    getattr(field_value, "generate_tool_functions")
                ):
                    sub_functions = getattr(field_value, "generate_tool_functions")(
                        prefix=prefix + "-" + self.name
                    )
                    all_functions += sub_functions
        return all_functions


class ValueField(Field, ABC):
    value: Any

    def set_value(self, val: Any):
        self.value = val

    def validate_value(self) -> bool:
        return True

    def setter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.name}-set_value"
        else:
            return f"{prefix}-{self.name}-set_value"

    @abstractmethod
    def data_type(self) -> str:
        pass

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        dct = {
            "type": "function",
            "function": {
                "name": self.setter_name(prefix),
                "description": f"Update the {self.name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "val": {
                            "type": self.data_type(),
                            "description": f"the new {self.name}",
                        },
                    },
                    "required": [self.name],
                },
            },
        }
        return [
            FunctionDescriptionPair(
                name=self.setter_name(prefix), fct=self.set_value, llm_description=dct
            )
        ]


class StringField(ValueField):
    value: Optional[str]

    def data_type(self) -> str:
        return "string"
    
class IntField(ValueField):
    value: Optional[int]

    def data_type(self) -> int:
        return "int"
    
class BoolField(ValueField):
    value: Optional[bool]

    def data_type(self) -> bool:
        return "bool"


class IPField(StringField):
    def validate(self):
        pass


class AbstractAppConfig(ABC, BaseModel):

    @abstractmethod
    def generate_prompt_string(self):
        pass

    def generate_tool_functions(self) -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_type in self.__dict__.items():
            field_value = getattr(self, field_name)
            if isinstance(field_value, Field):
                if hasattr(field_value, "generate_tool_functions") and callable(
                    getattr(field_value, "generate_tool_functions")
                ):
                    sub_functions = getattr(field_value, "generate_tool_functions")(
                        prefix=""
                    )
                    all_functions += sub_functions
        return all_functions
    
    
# TODO: Create specialized fields, think about which functions are generated for GPT, how updates are handled?    
    
class OPCUATagConfig(AbstractAppConfig):
    name: StringField
    address: StringField
    dataType: StringField
    acquisitionCycle: IntField
    acquisitionMode: StringField
    isArrayTypeTag: BoolField
    accessMode: StringField
    comments: StringField
    

class OPCUADatapointConfig(AbstractAppConfig):
    name: StringField
    tags: List[OPCUATagConfig]
    OPCUAUrl: IPField
    portNumber: IntField
    # TODO: Create separate field types for fields below cause they are in fact enums
    authenticationMode: IntField
    encryptionMode: IntField
    securityPolicy: IntField


class UAConnectorConfig(AbstractAppConfig):
    datapoints: List[OPCUADatapointConfig] # For S7, S7Plus change to collection of lists
    dbservicename: StringField
    # TODO: Maybe move authentication data somewhere else?
    username: StringField
    password: StringField
    
