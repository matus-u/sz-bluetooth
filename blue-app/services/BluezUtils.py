import dbus

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

def getManagedObjects():
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/"),
            "org.freedesktop.DBus.ObjectManager")
    return manager.GetManagedObjects()

def findAdapter():
    bus = dbus.SystemBus()
    obj = bus.get_object(SERVICE_NAME, '/org/bluez/hci0')
    return dbus.Interface(obj, ADAPTER_INTERFACE)

def scanDevices():
    return scanDevicesInObjects(getManagedObjects())

def scanDevicesInObjects(objects):
    bus = dbus.SystemBus()
    pathPrefix = findAdapter().object_path
    devices = []
    for path, ifaces in objects.items():
        device = ifaces.get(DEVICE_INTERFACE)
        if device is None:
            continue
        if path.startswith(pathPrefix):
            devices.append([path, device])
    return devices

def findDevice(deviceAddress):
    return findDeviceInScannedDevices(scanDevices(), deviceAddress)

def findDeviceInScannedDevices(objects, deviceAddress):
    bus = dbus.SystemBus()
    for path, device in objects:
        if (device["Address"] == deviceAddress):
            obj = bus.get_object(SERVICE_NAME, path)
            return dbus.Interface(obj, DEVICE_INTERFACE)
    raise Exception("Bluetooth device not found")

def removeDevice(deviceAddress):
    findAdapter().RemoveDevice(findDevice(deviceAddress))

def startDiscovery():
    properties_manager = dbus.Interface(findAdapter(), 'org.freedesktop.DBus.Properties')
    try:
        if properties_manager.Get(ADAPTER_INTERFACE, "Discovering") == 0:
            cleanupDevices()
            findAdapter().StartDiscovery()
    except:
        pass

def cleanupDevices():
    bus = dbus.SystemBus()
    adapter = findAdapter()
    for path, device in scanDevices():
        obj = bus.get_object(SERVICE_NAME, path)
        adapter.RemoveDevice(dbus.Interface(obj, DEVICE_INTERFACE))
