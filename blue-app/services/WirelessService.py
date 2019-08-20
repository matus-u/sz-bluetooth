from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings

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
    connectingSignal = QtCore.pyqtSignal()
    disconnectedSignal = QtCore.pyqtSignal()
    connectedSignal = QtCore.pyqtSignal()

    #private signals
    connectSignal = QtCore.pyqtSignal()
    disconnectSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state = "IDLE"

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

    #private API!
    def onStop(self):
        self.checkStatusTimer.stop()
        self.stopProcess()
        self.disconnect()

    def stopProcess(self):
        if self.state == "CONNECTING":
            self.process.disconnect()
            self.process.kill()
            self.process.waitForFinished()

    def onConnect(self):
        self.checkStatusTimer.stop()
        self.stopProcess()
        ssid = AppSettings.actualWirelessSSID()
        password = AppSettings.actualWirelessPassword()
        if not ssid is "":
            self.state = "CONNECTING"
            self.connectingSignal.emit()
            self.disconnect()
            self.process = QtCore.QProcess(self)
            self.process.finished.connect(self.onConnectFinished)
            self.process.start("scripts/wifi-connect.sh", [ ssid, password ])

    def onConnectFinished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.disconnectedSignal.emit()
            self.state = "DISCONNECTED"
            self.disconnect()
        else:
            self.connectedSignal.emit()
            self.state = "CONNECTED"

        self.checkStatusTimer.setSingleShot(True)
        self.checkStatusTimer.start(5000)

    def disconnect(self):
        QtCore.QProcess.execute("scripts/wifi-forget-connection.sh")
    
    def onTimer(self):
        if QtCore.QProcess.execute("scripts/wifi-state.sh") == 1:
            return self.onConnect()
        else:
            self.checkStatusTimer.setSingleShot(True)
            self.checkStatusTimer.start(5000)

