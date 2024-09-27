from Config import AbstractAppConfig


class App:
    """Class containing all data of an app including its Config"""

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
