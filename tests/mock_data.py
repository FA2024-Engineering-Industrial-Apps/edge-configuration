from src.models.abstract_config import AbstractAppConfig
from src.models.fields import StringField, NestedField, ListField


class AuthenticationData(NestedField):
    username: StringField = StringField(
        variable_name="username", description="the username of the user", value=None
    )

    password: StringField = StringField(
        variable_name="password", description="the users password", value=None
    )


class ContactInformation(NestedField):
    phone_number: StringField = StringField(
        variable_name="phone_number",
        description="the phone number of the user",
        value=None,
    )

    address: StringField = StringField(
        variable_name="address", description="the address of the user", value=None
    )


class ContactList(ListField):
    blueprint: ContactInformation = ContactInformation(
        variable_name="Contact_Information",
        description="The contact information of multiple user",
    )


# Look for default function signatures
class UserData(AbstractAppConfig):
    contacts: ContactList = ContactList(variable_name="contacts", description="The contact list")  # type: ignore
    name: StringField = StringField(
        variable_name="name", description="The name of the user", value=None
    )

    def generate_prompt_string(self):
        return "Needs a username and a string"
    
    def generate_prompt_sidebar(self):
        pass
