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
        self.connectionTimer = None


    def scan(self):
        BluezUtils.startDiscovery()
        devices = []
        for path, device in BluezUtils.scanDevices():
            devices.append ([device.get("Name", device["Address"]), "(" + str(device["Address"]) + ")"])
        return devices

    def afterMove(self):
        self.asyncConnectSignal.connect(self.connect, QtCore.Qt.QueuedConnection)
        self.asyncDisconnectSignal.connect(self.forceDisconnect, QtCore.Qt.QueuedConnection)

    def asyncConnect(self, macAddr, duration):
        self.asyncConnectSignal.emit(macAddr, duration)

    def asyncDisconnect(self):
        self.asyncDisconnectSignal.emit()

    def connect(self, macAddr, duration):
        if self.connectionTimer is None:
            self.connectionTimer = QtCore.QTimer()
            self.connectionTimer.setSingleShot(True)
            self.connectionTimer.timeout.connect(lambda: self.forceDisconnect())

        LoggingService.getLogger().info("Connect %s " % macAddr)
        self.duration = duration

        self.pairRequest = BluetoothAgent.PairRequest()
        self.pairRequest.connected.connect(self.onConnect)
        self.connectedDevice = macAddr
        self.pairRequest.pair(macAddr)

    def onConnect(self, exitCode):
        if exitCode == 1:
            self.connectedSignal.emit(exitCode)
            self.connectedDevice = ""
        else:
            self.connectionTimer.start(self.duration * 1000)
            self.connectedSignal.emit(0)

    def isConnected(self):
        return self.connectionTimer.isActive()

    def updateDuration(self, duration):
        self.connectionTimer.start(self.connectionTimer.remainingTime() + duration * 1000)
        LoggingService.getLogger().info("Update duration %s" %duration)

    def forceDisconnect(self):
        LoggingService.getLogger().info("FORCE DISCONNECT")
        self.connectionTimer.stop()
        self.disconnectedBeginSignal.emit()
        QtCore.QCoreApplication.processEvents()
        self.pairRequest.disconnect()
        self.connectedDevice = ""
        self.disconnectedEndSignal.emit()

    def getConnectedAddress(self):
        return str(self.connectedDevice)
