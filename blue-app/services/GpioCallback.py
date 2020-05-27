from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class GpioCallback(QtCore.QObject):
    callbackGpio = QtCore.pyqtSignal()
    internalCallbackGpio = QtCore.pyqtSignal()

    def __init__(self, parent, number, gpioService):
        super().__init__(parent)
        self.internalCallbackGpio.connect(lambda: self.callbackGpio.emit(), QtCore.Qt.QueuedConnection)
        gpioService.registerCallback(number, gpioService.FALLING, self.onLowLevelGpioInterrupt)

    def onLowLevelGpioInterrupt(self):
        self.internalCallbackGpio.emit()

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

        gpioService.registerCallback(number, gpioService.RISING, self.onLowLevelGpioUp)
        gpioService.registerCallback(number, gpioService.FALLING, self.onLowLevelGpioDown)

        self.gpioTimer.timeout.connect(self.onTimeout)

    def onTimeout(self):
        self.callbackGpio.emit()
        self.gpioTimer.start(self.contTime)

    def onLowLevelGpioUp(self):
        self.risingGpio.emit()

    def onLowLevelGpioDown(self):
        self.fallingGpio.emit()
