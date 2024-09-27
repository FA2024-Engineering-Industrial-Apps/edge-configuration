from typing import Callable, Dict

from pydantic.dataclasses import dataclass


@dataclass
class FunctionDescriptionPair:
    name: str
    fct: Callable[..., None]
    llm_description: Dict
