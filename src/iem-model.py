import abc


class Field(abc.ABC):
    name: str
    description: str

    def validate(self):
        pass


class StringField(Field):
    value: str


class IPField(StringField):
    def validate(self):
        # TODO
        pass


class IntegerField(Field):
    value: int


class PortField(IntegerField):
    def validate(self):
        # TODO
        pass


class AbstractAppConfig(abc.ABC):
    applicationName: str

    def generate_prompt_string(self):
        pass


class UAConnectorConfig(AbstractAppConfig):
    nameField: StringField
    ipField: IPField
    portField: PortField


class App:
    application_name: str
    config: AbstractAppConfig
