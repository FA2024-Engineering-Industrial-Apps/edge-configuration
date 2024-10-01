import pytest

from model.iem_model import AbstractAppConfig, StringField, NestedField, ListField
from .mock_data import UserData


def test_describe():
    dataObj = UserData()
    assert dataObj.describe() == {
        "contacts": {
            "variable_name": "contacts",
            "description": "The contact list",
            "items": [{'variable_name': 'Contact_Information', 'description': 'The contact information of multiple user', 'phone_number': {'variable_name': 'phone_number', 'description': 'the phone number of the user', 'value': None}, 'address': {'variable_name': 'address', 'description': 'the address of the user', 'value': None}}],
        },
        "name": {
            "variable_name": "name",
            "description": "The name of the user",
            "value": None,
        },
    }


def test_to_json():
    dataObj = UserData()
    assert dataObj.to_json() == {
        "contacts": [{'address': None, 'phone_number': None}],
        "name": None,
    }


def test_describe_hidden():
    dataObj = UserData()
    dataObj.name.visible = False
    assert dataObj.describe() == {
        "contacts": {
            "variable_name": "contacts",
            "description": "The contact list",
            "items": [{'variable_name': 'Contact_Information', 'description': 'The contact information of multiple user', 'phone_number': {'variable_name': 'phone_number', 'description': 'the phone number of the user', 'value': None}, 'address': {'variable_name': 'address', 'description': 'the address of the user', 'value': None}}],
        }
    }


def test_to_json_hidden():
    dataObj = UserData()
    assert dataObj.to_json() == {
        "contacts": [{'address': None, 'phone_number': None}],
        "name": None,
    }
