from devices import get_edge_devices

def conversation():
    print("Welcome to the Super-Smart-Edge-Helper! Here is a list of all available edge devices connected to the IEM:")
    
    edge_devices = get_edge_devices()
    for index, edge_device in enumerate(edge_devices):
        print(f"{index+1}: {edge_device['deviceName']} ({edge_device['deviceId']} - {edge_device["deviceStatus"]})")
    
    print()
    print("Which device do you want to act as the OPC-UA server?")
    
    server_id = int(input("(Please enter the index of the device) "))

    print(f"You selected {edge_devices[server_id-1]["deviceName"]}.")
    
    print()
    
    print("Which device do you want to connect to the server?")
    
    client = int(input("(Please enter the index of the device) "))

    print(f"You selected {edge_devices[client-1]["deviceName"]}.")
    print("The apps will now be installed...")
    
    
conversation()