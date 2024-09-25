from devices import get_edge_devices
from apps import install_app_on_edge_device

OPC_UA_SERVER_APP_ID = "fc4233dedbf948dda0c3f2f54001e525"
OPC_UA_CONNECTOR_APP_ID = "456e041339e744caa9514a1c86536067"


def conversation():
    print("Welcome to the Super-Smart-Edge-Helper! Here is a list of all available edge devices connected to the IEM:")
    
    edge_devices = get_edge_devices()
    for index, edge_device in enumerate(edge_devices):
        print(f"{index+1}: {edge_device['deviceName']} ({edge_device['deviceId']} - {edge_device["deviceStatus"]})")
    
    print()
    print("Which device do you want to act as the OPC-UA server?")
    
    server_id = int(input("(Please enter the index of the device) ")) -1
 
    print(f"You selected {edge_devices[server_id]["deviceName"]}.")
    
    print()
    
    print("Which device do you want to connect to the server?")
    
    client_id = int(input("(Please enter the index of the device) ")) - 1

    print(f"You selected {edge_devices[client_id]["deviceName"]}.")
    print()
    print("The apps will now be installed... This may take a minute")
    
    print("Installing OPC-UA server")
    server_result = install_app_on_edge_device(OPC_UA_SERVER_APP_ID, edge_devices[server_id]["deviceId"])
    if server_result["status"] == "LIVE":
        print(f"Successfully installed OPC-UA server on {edge_devices[server_id]["deviceName"]}")
    print()
    print("Installing OPC-UA client")
    client_result = install_app_on_edge_device(OPC_UA_CONNECTOR_APP_ID, edge_devices[client_id]["deviceId"])
    if client_result["status"] == "LIVE":
        print(f"Successfully installed OPC-UA connector on {edge_devices[client_id]["deviceName"]}")
    
conversation()