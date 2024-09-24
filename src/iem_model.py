from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict


@dataclass
class Field(ABC):
    name: str
    description: str

    @abstractmethod
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        pass


class NestedField(Field, ABC):
    pass

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

    def validate(self) -> bool:
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
                        "name": {
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


@dataclass
class StringField(ValueField):
    value: Optional[str]

    def data_type(self) -> str:
        return "string"


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


class UAConnectorConfig(AbstractAppConfig):
    ipField: IPField
