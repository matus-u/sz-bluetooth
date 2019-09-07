import dbus
import dbus.service
import dbus.mainloop.glib

from services.LoggingService import LoggingService

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


from services import BluezUtils
from PyQt5 import QtCore

AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"

class DeviceActionObject:
    def __init__(self, bus):
        self.bus = busAppSettings

    def setTrusted(self, path):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                        "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Device1", "Trusted", True)

    def setUnTrusted(self, path):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                        "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Device1", "Trusted", False)

    def devConnect(self, path):
        dev = dbus.Interface(self.bus.get_object("org.bluez", path),
                                "org.bluez.Device1")
        dev.Connect()
        LoggingService.getLogger().info("Dev connect %s" % path)

    def devDisconnect(self, path, address):
        dev = dbus.Interface(self.bus.get_object("org.bluez", path),
                                "org.bluez.Device1")
        dev.Disconnect()
        LoggingService.getLogger().info("Dev disconnect %s" % path)
        BluezUtils.removeDevice(address)

class PairRequest(QtCore.QObject):
    connected = QtCore.pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.mainloop = GObject.MainLoop()
        self.deviceActionObject = DeviceActionObject(dbus.SystemBus())

    def pair(self, deviceAddress):
        LoggingService.getLogger().info("Pair request %s " % deviceAddress)
        try:
            device = BluezUtils.findDevice(deviceAddress)
        except:
            LoggingService.getLogger().info("Cannot find device with id: " + deviceAddress)
            self.connected.emit(1)
            return
        self.devPath = device.object_path
        self.address = deviceAddress
        device.Pair(reply_handler=self.pairReply, error_handler=self.pairError,
                                timeout=15000)
        self.deviceObj = device
        self.mainloop.run()

    def pairReply(self):
        LoggingService.getLogger().info("Pair reply: %s" % self.devPath)
        self.deviceActionObject.setTrusted(self.devPath)
        self.deviceActionObject.devConnect(self.devPath)
        self.mainloop.quit()
        self.connected.emit(0)

    def pairError(self, error):
        errName = error.get_dbus_name()
        if errName == "org.freedesktop.DBus.Error.NoReply" and self.deviceObj:
            self.deviceObj.CancelPairing()
        else:
            LoggingService.getLogger().info("Creating device failed: %s" % (error))
        self.mainloop.quit()
        self.connected.emit(1)

    def disconnect(self):
        self.deviceActionObject.devDisconnect(self.devPath, self.address)


class Agent(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        dbus.service.Object.__init__(self, dbus.SystemBus(), AGENT_PATH)
        bus = dbus.SystemBus()
        self.deviceActionObject = DeviceActionObject(bus)
        obj = bus.get_object('org.bluez', "/org/bluez");
        manager = dbus.Interface(obj, "org.bluez.AgentManager1")
        manager.RegisterAgent(AGENT_PATH, "KeyboardDisplay")

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        pass
        self.deviceActionObject.setTrusted(device)
        return ""

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        self.deviceActionObject.setTrusted(device)
        return dbus.UInt32()

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        self.deviceActionObject.setTrusted(device)

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        pass

