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
        self.STATE = "IDLE"
        self.checkStatusTimer = QtCore.QTimer(self)
        self.checkStatusTimer.setSingleShot(True)
        self.checkStatusTimer.timeout.connect(self.onTimer)

        self.connectSignal.connect(self.onStop)
        self.disconnectSignal.connect(self.onConnect)

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.start()

    def stop():
        self.stop.emit()

    def connect():
        self.connect.emit()


    #private API!
    def onStop(self):
        self.checkStatusTimer.stop()
        if self.state == "CONNECTING":
            self.process.kill()
        self.disconnect()

    def onConnect(self):
        self.checkStatusTimer.stop()
        if self.state == "CONNECTING":
            self.process.kill()
        ssid = AppSettings.actualWirelessSSID()
        password = AppSettings.actualWirelessPassword()
        if not ssid is "":
            state = "CONNECTING"
            self.connectingSignal.emit()
            self.disconnect()
            self.process = QtCore.QProcess()
            self.process.finished.connect(self.onConnectFinished)
            self.process.start("scripts/wifi-connect.sh", [ ssid, password ])

    def onConnectFinished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.disconnectedSignal.emit()
            state = "DISCONNECTED"
            self.disconnect()
        else:
            self.connectedSignal.emit()
            state = "CONNECTED"

        self.checkStatusTimer.start(5000)
            

    def disconnect(self):
        QtCore.QProcess.execute("scripts/wifi-forget-connection.sh", [self.connectedDevice, self.connectedPid ])
    
    def onTimer(self):
        #TODO CHECK STATUS AND BASED ON IT RECONNECT/OR NEW TIMER
        self.checkStatusTimer.start(5000)

