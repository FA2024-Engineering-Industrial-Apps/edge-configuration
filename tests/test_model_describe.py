import pytest

from src.iem_model import AbstractAppConfig, StringField, NestedField, ListField
from .mock_data import UserData


def test_describe():
    dataObj = UserData()
    assert dataObj.describe() == {
        "contacts": {
            "variable_name": "contacts",
            "description": "The contact list",
            "items": [],
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
        "contacts": [],
        "name": None,
    }


def test_describe_hidden():
    dataObj = UserData()
    dataObj.name.visible = False
    assert dataObj.describe() == {
        "contacts": {
            "variable_name": "contacts",
            "description": "The contact list",
            "items": [],
        }
    }


def test_to_json_hidden():
    dataObj = UserData()
    assert dataObj.to_json() == {
        "contacts": [],
        "name": None,
    }


def test_from_json():
    dataObj = UserData()
    UserData.from_json(dataObj.to_json())
