from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService

class BluetoothStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(int)

    def __init__(self, duration):
        super().__init__(duration)

    def onTimeout(self):
        # TODO IMPLEMENT SPECIAL GET BLUETOOTH STATE
        self.actualStatus.emit(1)

class BluetoothService(QtCore.QObject):
    disconnectedBeginSignal = QtCore.pyqtSignal()
    disconnectedEndSignal = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)
    connectSignal = QtCore.pyqtSignal(int)

    def __init__(self, timerService):
        super().__init__()
        self.connectionTimer = QtCore.QTimer()
        self.connectionTimer.setSingleShot(True)
        self.connectionTimer.timeout.connect(lambda: self.forceDisconnect())
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(lambda: self.refreshTimerSignal.emit(int(self.connectionTimer.remainingTime()/1000)))

        self.statusObject = BluetoothStatusObject(1000)
        self.statusObject.actualStatus.connect(self.onSignalPower)
        timerService.addTimerWorker(self.statusObject)
        

    def scan(self):
        QtCore.QCoreApplication.processEvents()
        returnCode = QtCore.QProcess.execute("scripts/bt-scan.sh")
        processGetDevices = QtCore.QProcess()
        processGetDevices.start("scripts/bt-list-device.sh")
        if (processGetDevices.waitForFinished()):
            return processGetDevices.readAllStandardOutput().data().decode('utf-8').splitlines()
        return [] 


    def connect(self, macAddr, duration):
        self.duration = duration
        self.process = QtCore.QProcess()
        self.process.finished.connect(self.onConnect)
        self.process.start("scripts/bt-connect-with-timeout.sh", [ macAddr, "15" ])
        self.connectedDevice = macAddr

    def onConnect(self, exitCode, exitStatus):
        if exitCode == 1:
            self.connectSignal.emit(1)
            self.connectedDevice = ""
        else:
            self.connectedPid = self.process.readAllStandardOutput().data().decode('utf-8').splitlines()[-1]
            self.connectionTimer.start(self.duration * 1000)
            self.refreshTimerSignal.emit(int(self.connectionTimer.remainingTime()/1000))
            self.refreshTimer.start(1000)
            self.connectSignal.emit(0)
            self.statusObject.start()
        
    def forceDisconnect(self):
        self.statusObject.stop()
        self.connectionTimer.stop()
        self.refreshTimer.stop()
        self.disconnectedBeginSignal.emit()
        QtCore.QCoreApplication.processEvents()
        QtCore.QProcess.execute("scripts/bt-cleanup-device.sh", [self.connectedDevice, self.connectedPid ])
        self.disconnectedEndSignal.emit()

    def onSignalPower(self, value):
        print ("value " + str(value))

