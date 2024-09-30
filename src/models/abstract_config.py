from abc import ABC, abstractmethod
from pydantic import BaseModel
from .fields import Field, FunctionDescriptionPair
from typing import Dict, List


class AbstractAppConfig(ABC, BaseModel):

    @abstractmethod
    def generate_prompt_string(self):
        pass

    @abstractmethod
    def generate_prompt_sidebar(self):
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