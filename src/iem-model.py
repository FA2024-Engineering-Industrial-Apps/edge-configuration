import abc
from typing import Any, Dict


class Field(abc.ABC):
    name: str
    description: str
    value: Any

    def set_value(self, val: Any):
        self.value = val

    def validate(self) -> bool:
        return True

    def setter_name(self, prefix) -> str:
        return f"{prefix}.{self.name}.set_value"

    def generate_tool_function(self, prefix="") -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.setter_name(prefix),
                "description": f"Update the {self.name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": type(self.value),
                            "description": f"the new {self.name}",
                        },
                    },
                    "required": [self.name],
                },
            },
        }


class StringField(Field):
    value: str


class IPField(StringField):
    def validate(self):
        pass


class AbstractAppConfig(abc.ABC):
    def generate_prompt_string(self):
        pass


class UAConnectorConfig(AbstractAppConfig):
    ipField: IPField
