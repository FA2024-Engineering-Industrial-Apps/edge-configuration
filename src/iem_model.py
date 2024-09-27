from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
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


# For simplicity I assume that selector input is always a string
class EnumField(Field, ABC):
    mapping: Dict[str, Any]
    key: Any

    def validate_value(self, key: str) -> bool:
        return key in self.mapping.keys()

    def set_value(self, key: str):
        if self.validate_value(key):
            self.key = key
        else:
            # To be pushed
            raise ValidationException("Selector option is not available")

    def setter_name(self, prefix) -> str:
        if not prefix:
            return f"{self.variable_name}-set_value"
        else:
            return f"{prefix}-{self.variable_name}-set_value"

    def generate_tool_functions(self, prefix="") -> List[FunctionDescriptionPair]:
        if not self.setter_active:
            return []
        set_dct = {
            "type": "function",
            "function": {
                "name": self.setter_name(prefix),
                "description": f"Select value for selector {self.variable_name}. Available values are {' '.join(self.mapping.keys())}",
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
                "value": self.mapping[self.key],
            }
        else:
            return {}

    def to_json(self) -> Dict:
        if self.visible:
            return {"value": self.mapping[self.key]}
        else:
            return {}


class ListField(Field):
    items: List[Field] = []
    create_item_active: bool = True

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
        if not self.create_item_active:
            return []
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
                        new_prefix = prefix + "-" + self.variable_name
                    else:
                        new_prefix = self.variable_name
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
            return f"{self.variable_name}-set_value"
        else:
            return f"{prefix}-{self.variable_name}-set_value"

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
        return validators.url(val) == True


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


# TODO: Create specialized fields, think about which functions are generated for GPT, how updates are handled?
class OPCUATagAddressField(NestedField):
    namespace: IntField = IntField(
        variable_name="ns",
        description="Index of namespace for data within OPC UA Server",
        value=None,
    )
    nodeID: StringField = StringField(
        variable_name="s",
        description="ID of the data node within the OPC UA Server",
        value=None,
    )

    def to_json(self) -> Dict:
        if self.visible:
            return {"value": f"ns={self.namespace.value};s={self.nodeID.value}"}
        else:
            return {}

    def describe(self) -> Dict:
        if self.visible:
            return {
                "variable_name": self.variable_name,
                "description": self.description,
                "value": f"ns={self.namespace.value};s={self.nodeID.value}",
            }
        else:
            return {}


class OPCUATagConfig(NestedField):
    name: StringField = StringField(
        variable_name="name", description="Name of OPC UA Server data node", value=None
    )
    address: OPCUATagAddressField = OPCUATagAddressField(
        variable_name="address",
        description="Address of data within the OPC UA server. Consists of namespace index (ns) and node id (s).",
        nodeID=StringField(
            variable_name="nodeID",
            description="ID of the data node within the OPC UA server",
            value=None,
        ),
        namespace=IntField(
            variable_name="namespace",
            description="Index of namespace for data within OPC UA Server",
            value=None,
        ),
    )
    # EnumField?
    dataType: StringField = StringField(
        variable_name="dataType",
        description="""
        Type of data within the OPC UA server node. Available data types: Int, Bool, Byte, Char, DInt, String, 
        Real, Word, LInt, SInt, USInt, UInt, UDInt, ULInt, LReal, DWord, LWord. For array data add "Array" suffix to the type, e.g. "Int Array". 
        """,
        value=None,
    )
    acquisitionCycle: EnumField = EnumField(
        variable_name="acquisitionCycle",
        description="Time between consequent value checks in milliseconds or second. Available times: 10 milliseconds, 50 milliseconds, 100 milliseconds, 250 milliseconds, 500 milliseconds, 1 second, 2 second, 5 second, 10 second",
        key=None,
        mapping={
            "10 milliseconds": 10,
            "50 milliseconds": 50,
            "100 milliseconds": 100,
            "250 milliseconds": 250,
            "500 milliseconds": 500,
            "1 second": 1000,
            "2 second": 2000,
            "5 second": 5000,
            "10 second": 10000,
        },
    )
    acquisitionMode: EnumField = EnumField(
        variable_name="acquisitionMode",
        description="Aquisition mode, describing when UAConnector will pull value from data node. Possible options: CyclicOnChange",
        mapping={"CyclicOnChange": "CyclicOnChange"},
        key="CyclicOnChange",
    )
    isArrayTypeTag: BoolField = BoolField(
        variable_name="isArrayTypeTag",
        description="Boolean tag used to determine whether the data has an array type",
        value=None,
    )
    accessMode: EnumField = EnumField(
        variable_name="accessMode",
        description="Access mode of UA Connector to data node. Either Read, or Read & Write",
        key=None,
        mapping={"Read": "r", "Read & Write": "rw"},
    )
    comments: StringField = StringField(
        variable_name="comments",
        description="Comment describing the data transmitted from data node.",
        value=None,
    )


class OPCUADatapointConfig(NestedField):
    name: StringField = StringField(
        variable_name="name",
        description="The name of the corresponding OPC UA Server.",
        value=None,
    )
    tags: ListField = ListField(
        variable_name="tags",
        description="List of data nodes of the OPC UA server.",
        blueprint=OPCUATagConfig(
            variable_name="tag",
            description="Tag representing a data node of OPC UA Server",
        ),
    )
    OPCUAUrl: IPv6Field = IPv6Field(
        variable_name="OPCUAUrl",
        description="The URL of the corresponding OPC UA Server.",
        value=None,
    )
    portNumber: PortField = PortField(
        variable_name="portNumber",
        description="The port number from which the data of OPC UA Server will be sent.",
        value=None,
    )
    authenticationMode: EnumField = EnumField(
        variable_name="authenticationMode",
        key=None,
        description="Mode of authentication to OPC UA Server. Can be Anonymous or User ID & Password",
        mapping={"Anonymous": 1, "User ID & Password": 2},
    )


class DocumentationUAConnectorConfig(AbstractAppConfig):
    datapoints: ListField = ListField(
        variable_name="datapoints",
        description="List of OPC UA server configs that act as data sources.",
        blueprint=OPCUADatapointConfig(
            variable_name="OPCUAServer_Datapoint",
            description="OPC UA Server that sends data through this UA Connector",
        ),
    )  # For S7, S7Plus change to collection of lists
    dbservicename: StringField = StringField(
        variable_name="dbservicename",
        description="Name of the Databus service to which the data from UA Connector will be published",
        value=None,
    )
    # TODO: Create function for separate input of sensitive fields so they do not go through LLM
    username: StringField = StringField(
        variable_name="username",
        description="Username used to connect to Databus",
        value="edge",
    )
    password: StringField = StringField(
        variable_name="password",
        description="Password used to connect to Databus",
        value="edge",
    )


# definition of the UAConnector Config containing all data for the configuration of a UA Connector
class UAConnectorConfig(AbstractAppConfig):
    nameField: StringField = StringField(
        variable_name="Name",
        description="The name of the corresponding OPC UA Server.",
        value=None,
    )
    # Changed for testing TAKE THIS BACK!!!!!!!!!!!!!!!!!!!!!!!
    urlField: UrlField = UrlField(
        variable_name="OPC-UA_URL",
        description="The URL of the corresponding OPC UA Server.",
        value=None,
    )
    portField: PortField = PortField(
        variable_name="Port_number",
        description="The port number from which the data of OPC UA Server will be sent.",
        value=None,
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
            self.nameField.variable_name,
            self.nameField.description,
            self.nameField.value,
            self.urlField.variable_name,
            self.urlField.description,
            self.urlField.value,
            self.portField.variable_name,
            self.portField.description,
            self.portField.value,
        )

    def generate_prompt_sidebar(self):
        string = """
            
                
                Name: {0}
            
        
                
                URL: {1}
            
        
                
                Port number: {2}
            
        
        """
        return string.format(
            self.nameField.value,
            self.urlField.value,
            self.portField.value,
        )

class DocumentationDatabusConfig(AbstractAppConfig):
    userConfig: ListField = ListField(
        variable_name="user-config",
        description="List of users that are allowed to publish and subscribe to topics.",
        blueprint=DatabusUserConfig(
            variable_name="user",
            description="Databus user config."
        )
    )
    
# For testing TODO
class DatabusConfig(AbstractAppConfig):
    pass


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
        """.format(
            self.application_name,
            self.application_description,
            self.config.generate_prompt_string(),
        )
