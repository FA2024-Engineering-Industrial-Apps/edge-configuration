from .fields import StringField, ListField, NestedField
from .abstract_config import AbstractAppConfig

class OPCUAServerSource(NestedField):
    name: StringField = StringField(
        variable_name="name",
        description="Name of the data source.",
        value=None
    )
    userName: StringField = StringField(
        variable_name="userName",
        description="Username used to connect to data source",
        value=None
    )
    password: StringField = StringField(
        variable_name="password",
        description="Password used to connect to data source",
        value=None
    )
    topic: StringField = StringField(
        variable_name="topic",
        description="Topic through which the data relevant to the server is transferred",
        value=None
    )
    
class OPCUAServerConfig(AbstractAppConfig):
    sourceProviders: ListField = ListField(
        variable_name="sourceProviders",
        description="Data sources that send data fields to OPCUA Server",
        blueprint=OPCUAServerSource(
            variable_name="source",
            description="Single data source that sends data fields to server"
        )
    )