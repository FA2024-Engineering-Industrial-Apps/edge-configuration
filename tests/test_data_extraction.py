import pytest

from src.models.abstract_config import AbstractAppConfig
from src.models.fields import StringField, NestedField, ListField
from src.data_extraction import DataExtractor
from .mock_data_upa_config import UAConnectorConfig
from src.llm_service import GPT4Turbo


@pytest.mark.expensive
def test_extraction_scenario_1():
    dataObj = UAConnectorConfig()
    data_extractor = DataExtractor(dataObj, llm=GPT4Turbo())
    messages = [
        {
            "role": "system",
            "content": """
            You are an expert for configuring Siemens IEM.
            There are many different kinds of customers, some more experienced, but also beginners, which do not how to
            configure the IEM.
            The Siemens IEM eco system consists of different apps, which each have to be configured.
            Down below you find a list of all available apps in the IEM eco system.
            Do not use any other information about IEM you have except for the app list below.
            Each app consists of an "Appname", an "App-Description", which describes what the app does,
            and a config.
            Each config consists of fields, which have to be filled.
            Each field has a name, how the field is called in the user interface, and a description, what should be entered
            in this field.

            {0}

            You help the user to configure any app he wants to use.
            For this every field of every app config he wants to use has to be filled with a value.
            Ask the user for the values, and answer his questions about the apps and the fields.

            If there is nonsensical information for setting one of the values, skip this value but continue with the next one and call the setter function.
            """.format(
                dataObj.describe()
            ),
        },
        {
            "role": "user",
            "content": "How can you help me?",
        },
        {
            "role": "assistant",
            "content": """I can help you configure the apps in the Siemens IEM ecosystem by guiding you through filling out the necessary fields for each app. If you let me know which app you need to configure, I can ask you for the required values and provide explanations for what each field requires.
    For example, if you want to configure the "OPC UA Connector" app, I will need some specific information from you such as the name of the OPC UA Server, its URL, and the port number from which the data will be sent.
    Just let me know which app you want to configure, and I'll walk you through the process. If you have any questions about specific fields or the purpose of the app, feel free to ask!""",
        },
        {
            "role": "user",
            "content": "I want to configure the OPC UA Connector.",
        },
        {
            "role": "assistant",
            "content": """Great! Let's configure the "OPC UA Connector" app. I will need the following information from you to complete the configuration:
            Name: The name of the corresponding OPC UA Server.
            OPC-UA_URL: The URL of the corresponding OPC UA Server.
            Port_number: The port number from which the data of the OPC UA Server will be sent.
            Please provide the following details:

            Name: What is the name of the OPC UA Server?
            OPC-UA_URL: What is the URL of the OPC UA Server?
            Port_number: What is the port number used to send the data?
            Once you provide these details, I'll help you fill them in correctly.""",
        },
        {
            "role": "user",
            "content": "Set the OPC-UA_URL to http://timo.schmidt.de, set the name to Timo Schmidt and set the Port number to 15000000.",
        },
    ]

    data_extractor.update_data(messages)

    assert dataObj.nameField.value == "Timo Schmidt"
    assert dataObj.urlField.value == "http://timo.schmidt.de"
