from src.iem_model import (
    AbstractAppConfig,
    StringField,
    NestedField,
    ListField,
    IntField,
    UrlField,
    PortField,
    EnumField,
    IPv6Field,
    BoolField,
)

from typing import Dict, Any


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
        enum_key=None,
        enum_mapping={
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
        enum_mapping={"CyclicOnChange": "CyclicOnChange"},
        enum_key="CyclicOnChange",
    )
    isArrayTypeTag: BoolField = BoolField(
        variable_name="isArrayTypeTag",
        description="Boolean tag used to determine whether the data has an array type",
        value=None,
    )
    accessMode: EnumField = EnumField(
        variable_name="accessMode",
        description="Access mode of UA Connector to data node. Either Read, or Read & Write",
        enum_key=None,
        enum_mapping={"Read": "r", "Read & Write": "rw"},
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
        enum_key=None,
        description="Mode of authentication to OPC UA Server. Can be Anonymous or User ID & Password",
        enum_mapping={"Anonymous": 1, "User ID & Password": 2},
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
