from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from time import sleep
import os
from services import TimerService
from services.LoggingService import LoggingService

if os.getenv('RUN_FROM_DOCKER', False) == False:
    from services import BluezUtils
    from services import BluetoothAgent
else:
    from services.mocks import BluezUtils
    from services.mocks import BluetoothAgent

class BluetoothStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(int)

    def __init__(self, duration, getAddressCallback):
        super().__init__(duration)
        self.getAddressCallback = getAddressCallback

    def onTimeout(self):
        macAddr = self.getAddressCallback()
        if macAddr != "":
            processGetSignal = QtCore.QProcess()
            processGetSignal.start("scripts/bt-get-signal.sh", [ macAddr ])
            processGetSignal.waitForFinished()
            data = processGetSignal.readAllStandardOutput().data().decode('utf-8')
            if data != "NOT CONNECTED":
                self.actualStatus.emit(int(data))

class BluetoothService(QtCore.QObject):
    disconnectedBeginSignal = QtCore.pyqtSignal()
    disconnectedEndSignal = QtCore.pyqtSignal()
    connectedSignal = QtCore.pyqtSignal(int)
    connectionStrengthSignal = QtCore.pyqtSignal(int)

    asyncConnectSignal = QtCore.pyqtSignal(str, int)
    asyncDisconnectSignal = QtCore.pyqtSignal()

    def __init__(self, timerService):
        super().__init__()
        self.agent = BluetoothAgent.Agent()
        BluezUtils.startDiscovery()
        self.bluetoothSession = None

    def scan(self):
        BluezUtils.startDiscovery()
        devices = []
        for path, device in BluezUtils.scanDevices():
            devices.append ([device.get("Name", device["Address"]), "(" + str(device["Address"]) + ")"])
        return devices

    def afterMove(self):
        self.asyncConnectSignal.connect(self.connect, QtCore.Qt.QueuedConnection)
        self.asyncDisconnectSignal.connect(self.forceDisconnectFromUser, QtCore.Qt.QueuedConnection)

    def asyncConnect(self, macAddr, duration):
        self.asyncConnectSignal.emit(macAddr, duration)

    def asyncDisconnect(self):
        self.asyncDisconnectSignal.emit()

    def connect(self, macAddr, duration):
        if self.bluetoothSession:
            self.bluetoothSession.disconnectedEndSignal.disconnect(self.deviceDisconnected)
            self.bluetoothSession.connectedSignal.disconnect(self.connectedSignal)
            self.bluetoothSession.forceDisconnect()
        self.bluetoothSession = BluetoothSession()
        self.bluetoothSession.disconnectedEndSignal.connect(self.deviceDisconnected)
        self.bluetoothSession.connectedSignal.connect(self.connectedSignal)
        self.bluetoothSession.connect(macAddr, duration)


    def deviceConnectResult(self, status):
        self.connectedSignal.emit(status)

    def deviceDisconnected(self):
        self.bluetoothSession.disconnectedEndSignal.disconnect(self.deviceDisconnected)
        self.bluetoothSession.connectedSignal.disconnect(self.connectedSignal)
        self.bluetoothSession = None
        self.disconnectedBeginSignal.emit()
        self.disconnectedEndSignal.emit()

    def forceDisconnectFromUser(self, ):
        if self.bluetoothSession:
            self.bluetoothSession.forceDisconnect()



class BluetoothSession(QtCore.QObject):
    disconnectedEndSignal = QtCore.pyqtSignal()
    connectedSignal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.connectedDevice = ""
        self.duration = 0
        self.connectionTimer = None
        self.reconnectionTimer = QtCore.QTimer()
        self.reconnectionTimer.setSingleShot(True)
        self.reconnectionTimer.timeout.connect(self.reconnect)
        self.pairRequest = None

    def connect(self, macAddr, duration):
        if self.connectionTimer is None:
            self.connectionTimer = QtCore.QTimer()
            self.connectionTimer.setSingleShot(True)
            self.connectionTimer.timeout.connect(lambda: self.forceDisconnect())

        self.duration = duration
        self.connectedDevice = macAddr
        self.connectionTimer.start(self.duration * 1000)
        self.reconnect()

    def reconnect(self):
        LoggingService.getLogger().info("Connect %s " % self.connectedDevice)

        if self.pairRequest:
            self.pairRequest.connected.disconnect(self.onConnect)

        self.pairRequest = BluetoothAgent.PairRequest()
        self.pairRequest.connected.connect(self.onConnect)
        self.pairRequest.pair(self.connectedDevice)

    def onConnect(self, exitCode):
        if exitCode == 1:
            self.connectedSignal.emit(exitCode)
            if (self.connectionTimer.isActive()):
                self.reconnectionTimer.start(1000)
        else:
            self.connectionTimer.start(self.duration * 1000)
            self.connectedSignal.emit(0)

    def updateDuration(self, duration):
        self.connectionTimer.start(self.connectionTimer.remainingTime() + duration * 1000)
        LoggingService.getLogger().info("Update duration %s" %duration)

    def forceDisconnect(self):
        LoggingService.getLogger().info("Force disconnect")
        self.reconnectionTimer.stop()
        self.connectionTimer.stop()
        #QtCore.QCoreApplication.processEvents()
        self.pairRequest.connected.disconnect(self.onConnect)
        try:
            self.pairRequest.disconnect()
        except:
            pass

        self.connectedDevice = ""
        self.disconnectedEndSignal.emit()
        LoggingService.getLogger().info("After force disconnect")

