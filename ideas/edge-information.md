# Information on the industrial edge and its apps

The industrial edge is a platform produced by siemens, that is meant to be used to handle data and information flows in production environments. Different types of edge devices excist, which can be connected to PLCs, different cloud providers and other edge devices. The connection between the devices, PLCs and clouds is configured in the industrial edge management (IEM), which is a web interface. On each device different types of apps can be installed. Apps can be used to facilitate connections between devices, to configure dataflows within the device, to process data and for user interfaces about the data. An overview over the IEM, the different types of devices and apps is provided below. If there is a (not configurable) behind the type of app it is only non configurable by you, the assistant, but still configurable within the IEM.

## Industrial Edge Management

Industrial Edge Management serves as the central infrastructure for Industrial Edge, empowering organizations to leverage edge computing's potential to boost operational efficiency, minimize latency, enhance reliability, and expedite decision-making. By bringing intelligence and analytics capabilities closer to the data source, it enables quicker response times, improved resource allocation, and more efficient monitoring and control of industrial systems.

The industrial edge management can be used to connect edge devices to the industrial edge. It has an app catalog from which different apps can be installed on edge devices. The state of the connected edge devices can be checked, including the status (online/offline), hardware information, like the type of device, and the local IP adress of the device. Data about memory, CPU and storage use are provided.

The data connections between edge devices can be configured from the IEM. Depending on the use case different types of apps should be used. Information about the apps is provided below.

Information about different jobs is also provided on the IEM. Jobs in the context of IEM can be the installation of apps, uninstalling apps, updating apps or updating app configurations.

## Industrial Edge devices

There are different types of edge devices with different properties and capabilities.
Information about the devices is not proposed in detail here. A list of the available edge devices is given here:

## Apps on the industrial edge

### OPC-UA Server (not configurable)

The OPC-UA server uses the OPC-UA protocol to publish data in a local network. Multilpe devices can receive the data send out by the OPC-UA server. The data is most typically regular intervall timeseries data, such as sensor measurements. The different datapoints have to be defined in advance.

The official description is given here:
Edge OPC UA server application runs on Industrial Edge Device (IED) which provides open standard access to data that is available to the customers. Edge OPC UA server connects to the Databus for extracting the data. Any data source which supports Databus common payload format can be modeled in Edge OPC UA server. The application has two parts; Edge OPC UA Server Configurator and Edge OPC UA Server.

### OPC-UA Connector (configurable)

The OPC-UA connector connects an edge device to an opc-ua server. It can only receive data from the server and can not send any data. It uses the OPC-UA protocol. It can be either connected to an edge device with the OPC-UA server installed, or to other devices in the same network that use OPC-UA, such as integrated sensors.

### Databus (not configurable)

The databus application is used to publish data on one edge device. It has to be used to for example facilitate the data exchange between the OPC-UA connector and the cloud connector installed on one device. Every datapoint is specified as a topic, which is then referenced in other apps when trying to access that data.

The official description of the databus is given here:
The Databus provides access to the data of the field devices. The Industrial Edge Runtime sends the data from the field devices to the Databus. If you want to use this data for your custom application, you must connect your application to the Databus of the corresponding Industrial Edge Device (IED). Connectors are needed to fetch data from field devices. The configuration of the application is stored in the Databus, which allows the access of the app to the Databus.
The Databus consists of the following two components:

1. Databus Configurator in Industrial Edge Management:
The Databus Configurator in Industrial Edge Management includes a user interface. The Databus Configurator gives you an overview of the Databus-specific details of the corresponding Industrial Edge Device.

2. Databus:
The Databus is a distributed application that runs on the individual Industrial Edge Device. Data point values from the field devices are sent to the Databus. Additionally, you can configure own data points as required. You can use this application to access the data of the Databus for your individual applications.

3. Databus Provisioning Service (DPS):
Now Databus can also be configured through APIs using Databus Provisioning Service (DPS). For more deatils refer (Page 33)

### DataXess (not configurable)

DataXess makes data collection possible from different Edge devices and brings it to smart, intelligent and powerful applications for further analytics and processing.
DataXess is an IoT based application which collects data from different Edge devices and publishes data to any cloud application subscribing to it. It primarily facilitates device to device communication, which means data from low power and high power Edge devices are transmitted from multiple devices to a single device. Each Edge device collects data from sensors or field devices, and transmits data through Databus to DataXess. DataXess provides a solution to streamline data published from different Edge devices into a single Edge device through Databus.
DataXess application comprises of the following:
• Acquisition device - Any Edge device collecting real time data from sensors, field devices.
• Aggregator (Master) device - device which acts as a single communication link between multiple Edge devices. It is assigned to communicate and aggregate the data it receives into information through Databus.The information from the aggregator device is available on Databus and can be consumed by any application.
Devices are grouped and one of the device is assigned as an Aggregator device.

### Cloud connector (not configurable)

The Cloud Connector allows you to send data from your Industrial Edge Device to a cloud infrastructure, such as the Azure IoT Hub, or AWS IoT, or to a local infrastructure. All data is transmitted using the MQTT protocol and encrypted via TLS/SSL. The Cloud Connector consists of the following two components:

1. Cloud Connector Configurator:
With the Cloud Connector Configurator, you can configure Cloud Connector application installed in any IE Device, from your IEM.

2. Cloud Connector:
The Cloud Connector accesses data of the Databus from defined topics.

### Edgeshark (not configurable)

Discover and capture the virtual networking of your containers in your SIEMENS Industrial Edge devices.

See the virtual "wiring" and network configuration in your web browser. For instance, your container's IP and MAC addresses, their IP routing, and DNS configuration.

Easily capture your container network traffic with the SIEMENS Edgeshark plugin for the Wireshark network capture program. Simply install the Edgeshark plugin on your desktop system (Windows and Linux) and you are ready to capture. In the plugin, you see the containers running on your Industrial Edge device. Just click on the container you want to capture from.

### IEnsight (not configurable)

IEnsight offers a possibility to inspect and get more insight of containers running on a dedicated host.
For this, IEnsight leverages the Docker Daemon.
Currently, IEnsight offers the following features:

-> View all running containers on a host
-> Connect to a container's shell via web browser
-> View docker logs from a selected container
