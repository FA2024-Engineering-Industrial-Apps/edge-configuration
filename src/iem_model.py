from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict

# most general definition of a Field
class Field(ABC, BaseModel):
    name: str
    description: str

    @abstractmethod
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        pass

# general definition of a Field containing other Fields
class NestedField(Field, ABC):

    #generating a list containing all FunctionDescriptionPairs in all subfields of the nested field
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_value in self.__dict__.items():

            if isinstance(field_value, Field):
                if hasattr(field_value, "generate_tool_functions") and callable(
                        getattr(field_value, "generate_tool_functions")
                ):
                    sub_functions = getattr(field_value, "generate_tool_functions")(
                        # Example: results in subfield1.generate_tool_functions("-" + nestedField1.name)
                        # Case distinction necessary if prefix = "" ?????????????
                        prefix=prefix + "-" + self.name
                    )
                    all_functions += sub_functions
        return all_functions

# general definition of a field containing a single value
class ValueField(Field, ABC):
    value: Any

    def set_value(self, val: Any):
        self.value = val

    def get_value(self):
        return self.value

    def validate_value(self) -> bool:
        return True

    # returns a senseful name of the set_value function used for the llm description
    def setter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.name}-set_value"
        else:
            return f"{prefix}-{self.name}-set_value"

    def getter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.name}-get_value"
        else:
            return f"{prefix}-{self.name}-get_value"

    @abstractmethod
    def data_type(self) -> str:
        pass

    # returns a list containing the FunctionDescriptionPairs of the ValueField
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        set_dct = {
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
        get_dct = {
            "type": "function",
            "function": {
                "name": self.getter_name(prefix),
                "description": f"Gets the current value from {self.name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [self.name],
                },
            },
        }
        return [
            FunctionDescriptionPair(
                name=self.setter_name(prefix), fct=self.set_value, llm_description=set_dct
            ),
            FunctionDescriptionPair(
                name=self.getter_name(prefix), fct=self.get_value, llm_description=get_dct
            )
        ]


class StringField(ValueField):
    value: Optional[str]

    def data_type(self) -> str:
        return "string"


class IPField(StringField):
    pass


class IntegerField(ValueField):
    value: Optional[int]

    def data_type(self) -> str:
        return "integer"


class PortField(IntegerField):
    pass

# general definition an AppConfig - a datastructure containing the data for a certain configuration of an app
class AbstractAppConfig(ABC, BaseModel):

    @abstractmethod
    def generate_prompt_string(self):
        pass

    # returns a list containing the FunctionDescriptionPairs of all Fields and Subfields of the AppConfig
    def generate_tool_functions(self) -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Field):
                if hasattr(field_value, "generate_tool_functions") and callable(
                        getattr(field_value, "generate_tool_functions")
                ):
                    sub_functions = getattr(field_value, "generate_tool_functions")(
                        prefix=""
                    )
                    all_functions += sub_functions
        return all_functions

# definition of the UAConnector Config containing all data for the configuration of a UA Connector
class UAConnectorConfig(AbstractAppConfig):
    nameField: StringField = StringField(
            name="Name",
            description="The name of the corresponding OPC UA Server.",
            value=None
        )
    urlField: StringField = StringField(
            name="OPC-UA_URL",
            description="The URL of the corresponding OPC UA Server.",
            value=None
        )
    portField: PortField = PortField(
            name="Port_number",
            description="The port number from which the data of OPC UA Server will be sent.",
            value=None
        )

    # Using the defaul __init__() method of the AbstractAppConfig class with the values given in a dictionary
    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def generate_prompt_string(self):
        string = """
        [
            {{
                name: {0},
                description: {1},
                value: {2},
            }},
            {{
                name: {3},
                description: {4},
                value: {5},
            }},
            {{
                name: {6},
                description: {7},
                value: {8},
            }}
        ]
        """
        return string.format(
            self.nameField.name, self.nameField.description, self.nameField.value,
            self.urlField.name, self.urlField.description, self.urlField.value,
            self.portField.name, self.portField.description, self.portField.value
        )

# class containing all data of an app including its Config
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
        """.format(self.application_name, self.application_description, self.config.generate_prompt_string())
