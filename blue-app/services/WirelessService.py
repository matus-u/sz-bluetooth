from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings
from services.LoggingService import LoggingService

class WirelessScan(QtCore.QObject):
    def scan(self):
        QtCore.QCoreApplication.processEvents()
        processGetDevices = QtCore.QProcess()
        processGetDevices.start("scripts/wifi-list-ap.sh")
        if (processGetDevices.waitForFinished()):
            return processGetDevices.readAllStandardOutput().data().decode('utf-8').splitlines()
        return [] 

class WirelessService(QtCore.QObject):
    #report status signals
    stateChanged = QtCore.pyqtSignal(str, str)

    #private signals
    connectSignal = QtCore.pyqtSignal()
    disconnectSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state = "IDLE"
        self.ssid = ""

        self.checkStatusTimer = QtCore.QTimer()

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.checkStatusTimer.moveToThread(self.thread)
        self.thread.start()


        self.connectSignal.connect(self.onConnect, QtCore.Qt.QueuedConnection)
        self.disconnectSignal.connect(self.onStop, QtCore.Qt.QueuedConnection)
        self.checkStatusTimer.timeout.connect(self.onTimer)

    def stop(self):
        self.disconnectSignal.emit()

    def connect(self):
        self.connectSignal.emit()

    def start(self):
        if AppSettings.actualWirelessEnabled():
            self.connect()
        else:
            self.stop()

    #private API!
    def onStop(self):
        self.checkStatusTimer.stop()
        self.stopProcess()
        self.disconnect()
        self.state = "IDLE"
        self.stateChanged.emit(self.state, "")

    def stopProcess(self):
        if self.state == "CONNECTING":
            self.process.disconnect()
            self.process.kill()
            self.process.waitForFinished()

    def onConnect(self):
        LoggingService.getLogger().info("On Connect")
        self.checkStatusTimer.stop()
        self.stopProcess()
        self.ssid = AppSettings.actualWirelessSSID()
        password = AppSettings.actualWirelessPassword()
        if not self.ssid is "":
            self.state = "CONNECTING"
            self.stateChanged.emit(self.state, self.ssid)
            self.disconnect()
            self.process = QtCore.QProcess(self)
            self.process.finished.connect(self.onConnectFinished)
            LoggingService.getLogger().info("Connecting %s" % self.ssid)
            self.process.start("scripts/wifi-connect.sh", [ self.ssid, password ])

    def onConnectFinished(self, exitCode, exitStatus):
        LoggingService.getLogger().info("onConnectFinished %s" % str(exitCode))
        if exitCode != 0:
            self.state = "DISCONNECTED"
            self.stateChanged.emit(self.state, "")
            self.disconnect()
        else:
            self.state = "CONNECTED"
            self.stateChanged.emit(self.state, self.ssid)

        self.checkStatusTimer.setSingleShot(True)
        self.checkStatusTimer.start(5000)

    def disconnect(self):
        LoggingService.getLogger().info("Disconnect")
        QtCore.QProcess.execute("scripts/wifi-forget-connection.sh")
    
    def onTimer(self):
        if QtCore.QProcess.execute("scripts/wifi-state.sh") == 1:
            return self.onConnect()
        else:
            self.checkStatusTimer.setSingleShot(True)
            self.checkStatusTimer.start(5000)

