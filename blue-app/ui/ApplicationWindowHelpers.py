from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class NotStartSameImmediatellyCheck:
    def __init__(self):
        self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()
        self.lastStartedInfo = None

    def check(self, info):
        prevLastStarted = self.lastStarted
        self.lastStarted = QtCore.QDateTime.currentMSecsSinceEpoch()
        prevLastStartedInfo = self.lastStartedInfo
        self.lastStartedInfo = info
        if ((QtCore.QDateTime.currentMSecsSinceEpoch() - prevLastStarted) < 4000) and (self.lastStartedInfo == prevLastStartedInfo):
            return False
        return True

class StandardArrowHandler(QtCore.QObject):
    def __init__(self, parent, arrowHandler):
        super().__init__(parent)
        self.appWindow = parent
        self.arrowHandler = arrowHandler

        self.connectSignals()

    def connectSignals(self):
        self.arrowHandler.leftClicked.connect(self.onLeft)
        self.arrowHandler.rightClicked.connect(self.onRight)
        self.arrowHandler.downClicked.connect(self.onDown)
        self.arrowHandler.upClicked.connect(self.onUp)
        self.arrowHandler.confirmClicked.connect(self.onConfirm)

    def disconnectSignals(self):
        self.arrowHandler.leftClicked.disconnect(self.onLeft)
        self.arrowHandler.rightClicked.disconnect(self.onRight)
        self.arrowHandler.downClicked.disconnect(self.onDown)
        self.arrowHandler.upClicked.disconnect(self.onUp)
        self.arrowHandler.confirmClicked.disconnect(self.onConfirm)

    def onUp(self):
        self.appWindow.getActualFocusHandler().onUp()

    def onDown(self):
        self.appWindow.getActualFocusHandler().onDown()

    def onLeft(self):
        self.appWindow.getActualFocusHandler().onLeft()

    def onRight(self):
        self.appWindow.getActualFocusHandler().onRight()

    def onConfirm(self):
        self.appWindow.getActualFocusHandler().onConfirm()

class AppWindowArrowHandler(StandardArrowHandler):
    def __init__(self, parent, testModeService, arrowHandler):
        super().__init__(parent, arrowHandler)

        testModeService.testModeEnabled.connect(self.disconnectSignals)
        testModeService.testModeDisabled.connect(self.connectSignals)

    def connectSignals(self):
        super().connectSignals()
        self.arrowHandler.leftAndRightClicked.connect(self.onLeftRight)

    def disconnectSignals(self):
        super().disconnectSignals()
        self.arrowHandler.leftAndRightClicked.disconnect(self.onLeftRight)

    def onLeftRight(self):
        self.appWindow.focusLanguageChange()
