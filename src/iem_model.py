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

class NestedField(Field, ABC):


    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_value in self.__dict__.items():

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


class IPField(StringField):
    pass


class IntegerField(ValueField):
    value: Optional[int]

    def data_type(self) -> str:
        return "integer"


class PortField(IntegerField):
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
            self.nameField.name, self.nameField.description,
            self.urlField.name, self.urlField.description,
            self.portField.name, self.portField.description
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
        """.format(self.application_name, self.application_description, self.config.generate_prompt_string())
