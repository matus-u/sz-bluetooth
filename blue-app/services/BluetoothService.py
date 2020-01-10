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

    def __init__(self, timerService):
        super().__init__()
        self.connectionTimer = QtCore.QTimer()
        self.connectionTimer.setSingleShot(True)
        self.connectionTimer.timeout.connect(lambda: self.forceDisconnect())
        self.agent = BluetoothAgent.Agent()
        BluezUtils.cleanupDevices()
        BluezUtils.startDiscovery()

        self.statusObject = BluetoothStatusObject(1000, self.getConnectedAddress)
        self.statusObject.actualStatus.connect(lambda x: self.connectionStrengthSignal.emit(x))
        timerService.addTimerWorker(self.statusObject)

    def scan(self):
        sleep(2)
        devices = []
        for path, device in BluezUtils.scanDevices():
            devices.append ([device.get("Name", device["Address"]), "(" + str(device["Address"]) + ")"])
        return devices

    def connect(self, macAddr, duration):
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
            self.statusObject.start()

    def isConnected(self):
        return self.connectionTimer.isActive()

    def updateDuration(self, duration):
        self.connectionTimer.start(self.connectionTimer.remainingTime() + duration * 1000)
        LoggingService.getLogger().info("Update duration %s" %duration)
        
    def forceDisconnect(self):
        LoggingService.getLogger().info("FORCE DISCONNECT")
        self.statusObject.stop()
        self.connectionTimer.stop()
        self.disconnectedBeginSignal.emit()
        QtCore.QCoreApplication.processEvents()
        self.pairRequest.disconnect()
        self.connectedDevice = ""
        self.disconnectedEndSignal.emit()

    def getConnectedAddress(self):
        return str(self.connectedDevice)
