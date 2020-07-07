from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class DoubleButtonHandler(QtCore.QObject):
    bothClick = QtCore.pyqtSignal()
    internalCallbackGpio = QtCore.pyqtSignal()

    def __init__(self, parent, gpioService, firstGpioNumber, secondGpioNumber):
        super().__init__(parent)
        self.internalCallbackGpio.connect(lambda: self.bothClick.emit(), QtCore.Qt.QueuedConnection)
        self.buttonAPressed = False
        self.buttonBPressed = False

        gpioService.registerCallback(firstGpioNumber, gpioService.FALLING, lambda: self.onAChange(True))
        gpioService.registerCallback(secondGpioNumber, gpioService.FALLING, lambda: self.onBChange(True))

        gpioService.registerCallback(firstGpioNumber, gpioService.RISING, lambda: self.onAChange(False))
        gpioService.registerCallback(secondGpioNumber, gpioService.RISING, lambda: self.onBChange(False))

    def testBothClick(self):
        if self.buttonAPressed and self.buttonBPressed:
            self.internalCallbackGpio.emit()

    def onAChange(self, newState):
        self.buttonAPressed = newState
        self.testBothClick()

    def onBChange(self, newState):
        self.buttonBPressed = newState
        self.testBothClick()

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

class GpioTimedCallback(QtCore.QObject):

    callbackGpio = QtCore.pyqtSignal()
    risingGpio = QtCore.pyqtSignal()
    fallingGpio = QtCore.pyqtSignal()

    def __init__(self, parent, number, timeout, gpioService):
        super().__init__(parent)
        self.gpioTimer = QtCore.QTimer(self)
        self.gpioTimer.setSingleShot(True)
        self.timeout = timeout

        self.risingGpio.connect(lambda: self.gpioTimer.stop(), QtCore.Qt.QueuedConnection)
        self.fallingGpio.connect(lambda: self.gpioTimer.start(self.timeout), QtCore.Qt.QueuedConnection)

        gpioService.registerCallback(number, gpioService.FALLING, self.onLowLevelGpioUp)
        gpioService.registerCallback(number, gpioService.RISING, self.onLowLevelGpioDown)

        self.gpioTimer.timeout.connect(self.onTimeout)

    def onTimeout(self):
        self.callbackGpio.emit()
        self.gpioTimer.stop()

    def onLowLevelGpioUp(self):
        self.risingGpio.emit()

    def onLowLevelGpioDown(self):
        self.fallingGpio.emit()
