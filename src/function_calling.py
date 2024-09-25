from iem_model import AbstractAppConfig, StringField, NestedField, ListField
from data_extraction import DataExtractor
from llm_service import Mistral7b, Qwen25, Groq


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


dataObj = UserData()

extractor = DataExtractor(dataObj, llm=Groq())

messages = [
    {
        "role": "user",
        "content": "The name of the user is John Doe and he has 2 contacts.",
    }
]

extractor.update_data(messages)

messages_2 = [
    {
        "role": "user",
        "content": "The phone number of the first contact is 1234567890 and the address is 1234 Elm Street. For the second contact I only know the phone number which is 0987654321.",
    }
]

extractor.update_data(messages_2)

print(dataObj)
