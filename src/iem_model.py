import abc


class Field(abc.ABC):
    name: str
    description: str

    def validate(self):
        pass

    def __init__(self, name, description):
        self.name = name
        self.description = description


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

    def generate_prompt_string(self):
        pass


class UAConnectorConfig(AbstractAppConfig):
    nameField: StringField
    urlField: StringField
    portField: PortField

    def __init__(self):
        self.nameField = StringField(
            name="Name",
            description="The name of the corresponding OPC UA Server.",
        )
        self.urlField = StringField(
            name="OPC-UA URL",
            description="The URL of the corresponding OPC UA Server.",
        )
        self.portField = PortField(
            name="Port number",
            description="The port number from which the data of OPC UA Server will be sent.",
        )

    def generate_prompt_string(self):
        string = """
        [
            {{
                name: {0},
                description: {1},
            }},
            {{
                name: {2},
                description: {3},
            }},
            {{
                name: {4},
                description: {5},
            }}
        ]
        """
        return string.format(
            self.nameField.name, self.nameField.description,
            self.urlField.name, self.urlField.description,
            self.portField.name, self.portField.description
        )


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
        """.format(self.application_name, self.application_description, self.config.generate_prompt_string())
