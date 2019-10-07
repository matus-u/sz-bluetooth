from PyQt5 import QtCore

class AdminModeTracker(QtCore.QObject):

    adminModeInfoState = QtCore.pyqtSignal(bool)
    adminModeLeaveTime = QtCore.pyqtSignal(int)

    risingGpio = QtCore.pyqtSignal()
    fallingGpio = QtCore.pyqtSignal()

    def __init__(self, gpioService):
        super().__init__()
        self.state = False
        self.timer = QtCore.QTimer(self)
        self.refreshTimer = QtCore.QTimer(self)
        self.gpioTimer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.disableAdminMode())
        self.refreshTimer.timeout.connect(lambda: self.adminModeLeaveTime.emit(self.timer.remainingTime()/1000))
        self.gpioTimer.timeout.connect(lambda: self.enableAdminMode())

        self.risingGpio.connect(lambda: self.gpioTimer.stop(), QtCore.Qt.QueuedConnection)
        self.fallingGpio.connect(lambda: self.gpioTimer.start(3000), QtCore.Qt.QueuedConnection)

        GPIO_NUM = 37
        gpioService.registerBothCallbacks(GPIO_NUM, self.onLowLevelGpioInterrupt)

    def onLowLevelGpioInterrupt(self, isRising):
        if isRising:
            self.risingGpio.emit()
        else:
            self.fallingGpio.emit()

    def informAboutActualState(self):
        self.adminModeInfoState.emit(self.state)

    def changeAdminMode(self, enable):
        if self.state != enable:
            self.state = enable
            self.adminModeInfoState.emit(self.state)
            if self.state:
                self.refreshTimer.start(1000)
                self.timer.start(12000)
            else:
                self.timer.stop()
                self.refreshTimer.stop()

    def triggerAdminModeChange(self):
        self.changeAdminMode(not self.state)

    def enableAdminMode(self):
        self.changeAdminMode(True)

    def disableAdminMode(self):
        self.changeAdminMode(False)

