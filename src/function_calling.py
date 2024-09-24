from iem_model import AbstractAppConfig, StringField, NestedField
from data_extraction import DataExtractor


class AuthenticationData(NestedField):
    username: StringField = StringField(
        name="username", description="the username of the user", value=None
    )

    password: StringField = StringField(
        name="password", description="the users password", value=None
    )


# Look for default function signatures
class UserData(AbstractAppConfig):
    auth_data: AuthenticationData = AuthenticationData(
        name="authenticationdata", description="data for user auth"
    )

    email: StringField = StringField(
        name="email", description="The email of the user", value=None
    )

    def generate_prompt_string(self):
        return "Needs a username and a string"


dataObj = UserData()

extractor = DataExtractor(dataObj)

messages = [
    {
        "role": "user",
        "content": "I want to update my name to 'Niclas' and email to 'mymy@py.co' and password 123banana",
    }
]

extractor.update_data(messages)

print(dataObj)
