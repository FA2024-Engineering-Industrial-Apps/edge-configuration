from .fields import NestedField, StringField, EnumField, ListField, BoolField
from .abstract_config import AbstractAppConfig

class DatabusTopicConfig(NestedField):
    topic_name: StringField = StringField(
        variable_name="topic-name",
        description="Name of the MQQT topic a user can utilize for communication",
        value=None
    )
    access_rights: EnumField = EnumField(
        variable_name="access-rights",
        description="Access right of the user to the topic. Can be No Permission, Subscribe Only, Publish and Subscribe",
        key=None,
        mapping={"No Permission": "none", "Subscribe Only": "subscribe", "Publish and Subscribe": "both"}
    )
        
class DatabusUserConfig(NestedField):
    username: StringField = StringField(
        variable_name="username",
        description="Name of the Databus user.",
        value="edge"
    )
    password: StringField = StringField(
        variable_name="password",
        description="Password of the Databus user.",
        value=None
    )
    topics: ListField = ListField(
        variable_name="topics",
        description="List of MQTT topics that user can utilize for communication",
        blueprint=DatabusTopicConfig(
            variable_name="topic",
            description="Description of a single topic that user can use for communication"
        )
    )

class DatabusLiveViewConfig(NestedField):
    # TODO: Maybe more fields are necessary??
    topics: ListField = ListField(
        variable_name="topics",
        description="List of topic names that are monitored live.",
        blueprint=StringField(
            variable_name="topic-name",
            description="Name of the topic that is monitored live",
            value=None
        )
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
    # A separate persistence config may be needed
    persistence: BoolField = BoolField(
        variable_name="is-enabled",
        description="Bool flag showing whether data persistency is enabled for databus (passing messages are backuped).",
        value=None
    )
    autosave_interval: EnumField = EnumField(
        variable_name="autosave-interval",
        description="Time intervals between data backups in case persistency is enabled. Can be 5 mins, 1 hour, 1 day.",
        key=None,
        mapping={"5 mins": "300", "1 hour": "3600", "1 day": "86400"}
    )
    live_view_config: DatabusLiveViewConfig = DatabusLiveViewConfig(
        variable_name="live_view_config",
        description="Config for live monitoring of communication through MQTT topics."
    )