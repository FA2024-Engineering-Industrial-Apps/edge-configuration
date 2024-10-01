import pytest

from src.iem_integration.config_converter import ConfigConverter, AppType
from src.iem_integration.devices import DetailedDevice
from src.model.iem_model import DocumentationUAConnectorConfig


def test_config_converter_opc_ua_connector():
    config_converter = ConfigConverter("../src/iem_integration/configs")

    connector = DocumentationUAConnectorConfig()

    connector.username.set_value("edge")
    connector.password.set_value("password")
    connector.datapoints.create_item()
    connector.datapoints.items[0].name.set_value("name")
    connector.datapoints.items[0].tags.create_item()
    connector.datapoints.items[0].tags.items[0].address.namespace.set_value(1)
    connector.datapoints.items[0].tags.items[0].address.nodeID.set_value("test")

    device = DetailedDevice(
        id="1",
        name="testDev",
        url="www.gmx.de",
        status="0"
    )

    res = config_converter.convert_to_iem_json(connector.to_json(), device, AppType.OPC_UA_CONNECTOR)
    print(res)
