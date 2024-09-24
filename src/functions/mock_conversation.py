from devices import get_edge_devices

def conversation():
    print("Welcome to the Super-Smart-Edge-Helper! Here is a list of all available edge devices connected to the IEM:")
    
    edge_devices = get_edge_devices()
    for index, edge_device in enumerate(edge_devices):
        print(f"{index+1}: {edge_device['deviceName']} ({edge_device['deviceId']} - {edge_device["deviceStatus"]})")
    
    print("Which edge device do you want to configure? Please enter a the device id!")
    dev_id = input("")
    print(f"This is the device id you selected {dev_id}")
    
conversation()