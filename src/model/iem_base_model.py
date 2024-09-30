from __future__ import annotations
from abc import ABC, abstractmethod

# from builtins import classmethod
from typing import Any, Dict, List, Callable, Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from error_handling import ValidationException
import validators


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict


# most general definition of a Field
class Field(ABC, BaseModel):
    variable_name: str
    description: str

    setter_active: bool = True
    visible: bool = True

    @abstractmethod
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        pass

    def deactivate_setter(self):
        self.setter_active = False

    def activate_setter(self):
        if self.visible:
            self.setter_active = True

    def set_visible(self):
        self.visible = True

    def set_invisible(self):
        self.visible = False
        self.setter_active = False

    @abstractmethod
    def describe(self) -> Dict:
        pass

    @abstractmethod
    def to_json(self) -> Dict:
        pass

    @abstractmethod
    def fill_from_json(self, json: Any):
        pass


# For simplicity I assume that selector input is always a string
class EnumField(Field, ABC):
    enum_mapping: Dict[str, Any]
    enum_key: Any

    def validate_value(self, key: str) -> bool:
        return key in self.enum_mapping.keys()

    def set_value(self, key: str):
        if self.validate_value(key):
            self.key = key
        else:
            # To be pushed
            raise ValidationException("Selector option is not available")

    def setter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.variable_name.replace(' ', '_')}-set_value"
        else:
            return f"{prefix}-{self.variable_name.replace(' ', '_')}-set_value"

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        if not self.setter_active:
            return []
        set_dct = {
            "type": "function",
            "function": {
                "name": self.setter_name(prefix),
                "description": f"Select value for selector {self.variable_name}. Available values are {' '.join(self.enum_mapping.keys())}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "val": {
                            "type": "string",
                            "description": f"Selected option from selector {self.variable_name}",
                        },
                    },
                    "required": [self.variable_name],
                },
            },
        }
        return [
            FunctionDescriptionPair(
                name=self.setter_name(prefix),
                fct=self.set_value,
                llm_description=set_dct,
            )
        ]

    def describe(self) -> Dict:
        if self.visible:
            return {
                "variable_name": self.variable_name,
                "description": self.description,
                "value": self.enum_mapping[self.enum_key] if self.enum_key else None,
            }
        else:
            return {}

    def to_json(self) -> Dict:
        if self.visible:
            return {"value": self.enum_mapping[self.enum_key] if self.enum_key else None}
        else:
            return {}

    # Idk how this enum works
    def fill_from_json(self, json: Any):
        for k, v in self.enum_mapping.items():
            if v == json:
                self.enum_key = k
                return
        raise ValueError(f"No matching key found for {json}")


class ListField(Field):
    items: List[Field] = []
    create_item_active: bool = True

    blueprint: Field

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.items.append(self.blueprint.model_copy(deep=True))

    def create_item(self):
        self.items.append(self.blueprint.model_copy(deep=True))


    def create_prefix(self, preprefix: str) -> str:
        if preprefix == "":
            return self.variable_name
        return f"{preprefix}-{self.variable_name}"

    def type_name(self) -> str:
        return type(self.blueprint).__name__

    def generate_create_function(self, prefix="") -> List[FunctionDescriptionPair]:
        if not self.create_item_active:
            return []
        name = self.create_item_name(prefix)
        fct = self.create_item
        llm_description = {
            "type": "function",
            "function": {
                "name": name,
                "description": f"Create a new entry for {self.blueprint.variable_name} of type {self.type_name()}",
                "parameters": {},
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
            if prefix:
                new_prefix = f"{prefix}-{idx}"
            else:
                new_prefix = f"{idx}"
            lst = i.generate_tool_functions(prefix=new_prefix)
            all_pairs += lst
        all_pairs += self.generate_create_function(prefix=prefix)
        return all_pairs

    def deactivate_setter(self):
        for i in self.items:
            i.deactivate_setter()

    def activate_setter(self):
        for i in self.items:
            i.activate_setter()

    def describe(self) -> Dict:
        if self.visible:
            return {
                "variable_name": self.variable_name,
                "description": self.description,
                "items": [item.describe() for item in self.items if item.visible],
            }
        else:
            return {}

    def to_json(self) -> Dict:
        if self.visible:
            return {"value": [i.to_json()["value"] for i in self.items]}
        else:
            return {}

    def fill_from_json(self, json: Any):
        if isinstance(json, list):
            for i in json:
                new_item = self.blueprint.model_copy(deep=True)
                new_item.fill_from_json(i)
                self.items.append(new_item)


# general definition of a Field containing other Fields
class NestedField(Field, ABC):

    # generating a list containing all FunctionDescriptionPairs in all subfields of the nested field
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        all_functions = []
        for field_name, field_value in self.__dict__.items():

            if isinstance(field_value, Field):
                if hasattr(field_value, "generate_tool_functions") and callable(
                    getattr(field_value, "generate_tool_functions")
                ):
                    if prefix:
                        new_prefix = prefix + "-" + self.variable_name.replace(" ", "_")
                    else:
                        new_prefix = self.variable_name.replace(" ", "_")
                    sub_functions = getattr(field_value, "generate_tool_functions")(
                        new_prefix
                    )
                    all_functions += sub_functions
        return all_functions

    def deactivate_setter(self):
        for _, field_value in self.__dict__.items():

            if isinstance(field_value, Field):
                if hasattr(field_value, "deactivate_setter") and callable(
                    getattr(field_value, "deactivate_setter")
                ):
                    getattr(field_value, "deactivate_setter")()

    def activate_setter(self):
        for _, field_value in self.__dict__.items():

            if isinstance(field_value, Field):
                if hasattr(field_value, "activate_sette") and callable(
                    getattr(field_value, "activate_sette")
                ):
                    getattr(field_value, "activate_setter")()

    def describe(self) -> Dict:
        base: Dict = {}
        if not self.visible:
            return base

        base["variable_name"] = self.variable_name
        base["description"] = self.description

        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Field):
                if field_value.visible:
                    base[field_name] = field_value.describe()
        return base

    def to_json(self) -> Dict:
        if not self.visible:
            return {"value": {}}

        base: Dict = {}

        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Field):
                if field_value.visible:
                    base[field_name] = field_value.to_json()["value"]
        return {"value": base}

    def fill_from_json(self, json: Any):
        if isinstance(json, dict):
            for k, v in self.__dict__.items():
                if k in json:
                    v.fill_from_json(json[k])
        else:
            raise ValueError(f"NestedField could not be created from {json}")


# general definition of a field containing a single value
class ValueField(Field, ABC):
    value: Any

    def set_value(self, val: Any):
        if self.validate_value(val):
            self.value = val
        else:
            raise ValidationException("Value Validation failed / yielded false.")

    def validate_value(self, val) -> bool:
        return val is not None

    # returns a senseful name of the set_value function used for the llm description
    def setter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.variable_name.replace(' ', '_')}-set_value"
        else:
            return f"{prefix}-{self.variable_name.replace(' ', '_')}-set_value"

    @abstractmethod
    def data_type(self) -> str:
        pass

    # returns a list containing the FunctionDescriptionPairs of the ValueField
    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        if not self.setter_active:
            return []
        set_dct = {
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
                name=self.setter_name(prefix),
                fct=self.set_value,
                llm_description=set_dct,
            )
        ]

    def describe(self) -> Dict:
        if self.visible:
            return {
                "variable_name": self.variable_name,
                "description": self.description,
                "value": self.value,
            }
        else:
            return {}

    def to_json(self) -> Dict:
        if self.visible:
            return {"value": self.value}
        else:
            return {}

    def fill_from_json(self, json: Any):
        self.set_value(json)


class StringField(ValueField):
    value: Optional[str]

    def data_type(self) -> str:
        return "string"


class IntField(ValueField):
    value: Optional[int]

    def data_type(self) -> str:
        return "integer"


class BoolField(ValueField):
    value: Optional[bool]

    def data_type(self) -> str:
        return "bool"


class IPField(StringField):

    def validate_value(self, val) -> bool:
        return validators.ipv4(val) == True or validators.ipv6(val) == True


class IPv4Field(IPField):

    def validate_value(self, val) -> bool:
        return validators.ipv4(val) == True


class IPv6Field(IPField):

    def validate_value(self, val) -> bool:
        return validators.ipv6(val) == True


class PortField(IntField):

    def validate_value(self, val) -> bool:
        return 0 <= val <= 65535  # type: ignore


class EmailField(StringField):

    def validate_value(self, val) -> bool:
        return validators.email(val) == True


class UrlField(StringField):

    def validate_value(self, val) -> bool:
        # return validators.url(val) == True
        # TODO: URL validation too harsh
        return True


class AbstractAppConfig(ABC, BaseModel):

    def generate_prompt_string(self):
        return str(self.describe())

    def generate_prompt_sidebar(self):
        json_description = self.describe()
        result_string = ""
        for field, value in json_description.items():
            result_string += f"{field}: {value}\n"
        return result_string

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

    def describe(self) -> Dict:
        base: Dict = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Field):
                if field_value.visible:
                    base[field_name] = field_value.describe()
        return base

    def to_json(self) -> Dict:
        base: Dict = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Field):
                if field_value.visible:
                    base[field_name] = field_value.to_json()["value"]
        return base

    def fill_from_json(self, json: Dict):
        for k, v in self.__dict__.items():
            if k in json:
                v.fill_from_json(json[k])
