import pytest

from src.iem_model import AbstractAppConfig, StringField, NestedField, ListField
from .mock_data import UserData


def test_load_from_export():
    dataObj = UserData()
    dataObj.name.set_value("Carl")
    dataObj.contacts.create_item(1)
    dataObj.contacts.items[0].phone_number.set_value("123456789")
    dataObj.contacts.items[0].address.set_value("Siemensstr. 1")

    dct = dataObj.to_json()

    dataObj2 = UserData()

    dataObj2.fill_from_json(dct)

    assert dataObj2.name.value == "Carl"
    assert dataObj2.contacts.items[0].phone_number.value == "123456789"
    assert dataObj2.contacts.items[0].address.value == "Siemensstr. 1"
