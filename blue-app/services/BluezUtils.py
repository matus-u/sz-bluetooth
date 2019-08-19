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
    return findAdapterInObjects(getManagedObjects())

def findAdapterInObjects(objects):
    bus = dbus.SystemBus()
    for path, ifaces in objects.items():
        adapter = ifaces.get(ADAPTER_INTERFACE)
        obj = bus.get_object(SERVICE_NAME, path)
        return dbus.Interface(obj, ADAPTER_INTERFACE)
    raise Exception("Bluetooth adapter not found")

def scanDevices():
    return scanDevicesInObjects(getManagedObjects())

def scanDevicesInObjects(objects):
    bus = dbus.SystemBus()
    pathPrefix = ""
    adapter = findAdapterInObjects(objects)
    pathPrefix = adapter.object_path
    devices = []
    for path, ifaces in objects.items():
        device = ifaces.get(DEVICE_INTERFACE)
        if device is None:
            continue
        if path.startswith(pathPrefix):
            devices.append([path, device])
    return devices

def findDevice(device_address):
    return findDeviceInScannedDevices(scanDevices(), device_address)

def findDeviceInScannedDevices(objects, deviceAddress):
    for path, device in objects:
        if (device["Address"] == deviceAddress):
            obj = bus.get_object(SERVICE_NAME, path)
            return dbus.Interface(obj, DEVICE_INTERFACE)
    raise Exception("Bluetooth device not found")

