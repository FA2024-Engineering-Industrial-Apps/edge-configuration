import pytest

from model.iem_model import AbstractAppConfig, StringField, NestedField, ListField
from llm_integration.data_extraction import DataExtractor
from .mock_data import AuthenticationData, ContactInformation, ContactList, UserData


def test_function_generation():
    dataObj = UserData()
    extractor = DataExtractor(dataObj)
    assert len(extractor.tool_descriptions) == 4

    dataObj.contacts.create_item()
    extractor._refresh_tools()

    assert len(extractor.tool_descriptions) == 6


def test_hidden_setter():
    dataObj = UserData()
    extractor = DataExtractor(dataObj)
    assert len(extractor.tool_descriptions) == 4

    dataObj.name.deactivate_setter()
    extractor._refresh_tools()

    assert len(extractor.tool_descriptions) == 3
