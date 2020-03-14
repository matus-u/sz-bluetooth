from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class GpioCallback(QtCore.QObject):
    callbackGpio = QtCore.pyqtSignal()

    def __init__(self, parent, number, gpioService):
        super().__init__(parent)
        gpioService.registerCallback(gpioService.FALLING, number, self.onLowLevelGpioInterrupt)

    def onLowLevelGpioInterrupt(self, channel):
        self.callbackGpio.emit()

class GpioCallbackContinous(QtCore.QObject):

    callbackGpio = QtCore.pyqtSignal()
    risingGpio = QtCore.pyqtSignal()
    fallingGpio = QtCore.pyqtSignal()

    def __init__(self, parent, number, timeCont, gpioService):
        super().__init__(parent)
        self.gpioTimer = QtCore.QTimer(self)
        self.contTime = timeCont
        self.risingGpio.connect(lambda: self.gpioTimer.stop(), QtCore.Qt.QueuedConnection)
        self.fallingGpio.connect(self.onTimeout, QtCore.Qt.QueuedConnection)
        gpioService.registerBothCallbacks(number, self.onLowLevelGpioInterrupt)
        self.gpioTimer.timeout.connect(self.onTimeout)

    def onTimeout(self):
        self.callbackGpio.emit()
        self.gpioTimer.start(contTime)

    def onLowLevelGpioInterrupt(self, isRising):
        if isRising:
            self.risingGpio.emit()
        else:
            self.fallingGpio.emit()
