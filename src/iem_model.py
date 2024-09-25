from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
from typing_extensions import Unpack
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, ConfigDict


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict


class Field(ABC, BaseModel):
    variable_name: str
    description: str

    @abstractmethod
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        pass


class ListField(Field):
    items: List[Field] = []

    blueprint: Field

    def create_item(self, number: int):
        for i in range(number):
            self.items.append(self.blueprint.model_copy(deep=True))

    def create_prefix(self, preprefix: str) -> str:
        if preprefix == "":
            return self.variable_name
        return f"{preprefix}-{self.variable_name}"

    def type_name(self) -> str:
        return type(self.blueprint).__name__

    def generate_create_function(self, prefix="") -> List[FunctionDescriptionPair]:
        name = self.create_item_name(prefix)
        fct = self.create_item
        llm_description = {
            "type": "function",
            "function": {
                "name": name,
                "description": f"Create a new entries for {self.blueprint.variable_name} of type {self.type_name()}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "type": "integer",
                            "description": f"Amount of new {self.type_name()} to create",
                        },
                    },
                    "required": [self.variable_name],
                },
            },
        }
        return [
            FunctionDescriptionPair(name=name, fct=fct, llm_description=llm_description)
        ]

    def create_item_name(self, prefix: str) -> str:
        if prefix == "":
            return f"{self.variable_name}-create_item"
        else:
            return f"{prefix}-{self.variable_name}-create_item"

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        all_pairs = []
        for idx, i in enumerate(self.items):
            lst = i.generate_tool_functions(prefix=f"{prefix}-{idx}")
            all_pairs += lst
        all_pairs += self.generate_create_function(prefix=prefix)
        return all_pairs


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
                        prefix=prefix + "-" + self.variable_name
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
            return f"{self.variable_name}-set_value"
        else:
            return f"{prefix}-{self.variable_name}-set_value"

    @abstractmethod
    def data_type(self) -> str:
        pass

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        dct = {
            "type": "function",
            "function": {
                "name": self.setter_name(prefix),
                "description": f"Update the {self.variable_name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "val": {
                            "type": self.data_type(),
                            "description": f"the new {self.variable_name}",
                        },
                    },
                    "required": [self.variable_name],
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

    def data_type(self) -> str:
        return "int"


class BoolField(ValueField):
    value: Optional[bool]

    def data_type(self) -> str:
        return "bool"


class IPField(StringField):
    pass


class PortField(IntField):
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


class OPCUATagConfig(NestedField):
    name: StringField
    address: StringField
    dataType: StringField
    acquisitionCycle: IntField
    acquisitionMode: StringField
    isArrayTypeTag: BoolField
    accessMode: StringField
    comments: StringField


class OPCUADatapointConfig(NestedField):
    name: StringField = StringField(
        variable_name="Name",
        description="The name of the corresponding OPC UA Server.",
        value=None,
    )
    tags: List[OPCUATagConfig] = []
    OPCUAUrl: StringField = StringField(
        variable_name="OPC-UA_URL",
        description="The URL of the corresponding OPC UA Server.",
        value=None,
    )
    portNumber: IntField = IntField(
        variable_name="Port_number",
        description="The port number from which the data of OPC UA Server will be sent.",
        value=None,
    )
    # TODO: Create separate field types for fields below cause they are in fact enums
    authenticationMode: IntField
    encryptionMode: IntField
    securityPolicy: IntField


class DocumentationUAConnectorConfig(AbstractAppConfig):
    datapoints: List[
        OPCUADatapointConfig
    ]  # For S7, S7Plus change to collection of lists
    dbservicename: StringField
    # TODO: Maybe move authentication data somewhere else?
    username: StringField
    password: StringField


class UAConnectorConfig(AbstractAppConfig):
    nameField: StringField = StringField(
        variable_name="Name",
        description="The name of the corresponding OPC UA Server.",
        value=None,
    )
    urlField: StringField = StringField(
        variable_name="OPC-UA_URL",
        description="The URL of the corresponding OPC UA Server.",
        value=None,
    )
    portField: PortField = PortField(
        variable_name="Port_number",
        description="The port number from which the data of OPC UA Server will be sent.",
        value=None,
    )

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def generate_prompt_string(self):
        string = """
        [
            {{
                name: {0},
                description: {1},
            }},
            {{
                name: {2},
                description: {3},
            }},
            {{
                name: {4},
                description: {5},
            }}
        ]
        """
        return string.format(
            self.nameField.name,
            self.nameField.description,
            self.urlField.name,
            self.urlField.description,
            self.portField.name,
            self.portField.description,
        )


class App:
    application_name: str
    application_description: str
    config: AbstractAppConfig

    def __init__(self, name: str, description: str, config: AbstractAppConfig):
        self.application_name = name
        self.application_description = description
        self.config = config

    def generate_prompt_string(self) -> str:
        return """
        {{
            app-name: {0},
            app-description: {1},
            fields: {2}
        }}
        """.format(
            self.application_name,
            self.application_description,
            self.config.generate_prompt_string(),
        )
