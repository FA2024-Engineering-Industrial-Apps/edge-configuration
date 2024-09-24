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


class AbstractAppConfig(abc.ABC):
    def generate_prompt_string(self):
        pass


class UAConnectorConfig(AbstractAppConfig):
    ipField: IPField



