import pytest

from src.models.iem_model import AbstractAppConfig, StringField, NestedField, ListField
from src.data_extraction import DataExtractor
from .mock_data import AuthenticationData, ContactInformation, ContactList, UserData


def test_function_generation():
    dataObj = UserData()
    extractor = DataExtractor(dataObj)
    assert len(extractor.tool_descriptions) == 2

    dataObj.contacts.create_item(2)
    extractor._refresh_tools()

    assert len(extractor.tool_descriptions) == 6


def test_hidden_setter():
    dataObj = UserData()
    extractor = DataExtractor(dataObj)
    assert len(extractor.tool_descriptions) == 2

    dataObj.name.deactivate_setter()
    extractor._refresh_tools()

    assert len(extractor.tool_descriptions) == 1
