from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys, os

import ApplicationWindow

from services.AppSettings import AppSettings
from services.TimerService import TimerService
from services.UpdateStatus import WebSocketStatus
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker
from services.AdminModeTracker import AdminModeTracker

if os.getenv('RUN_FROM_DOCKER', False) == False:
    from services.GpioService import GpioService
else:
    from services.mocks.GpioService import GpioService

def connectAdminModeTracker(adminModeTracker, applicationWindow, webUpdateStatus):

    adminModeTracker.adminModeInfoState.connect(webUpdateStatus.onAdminModeLocalChange, QtCore.Qt.QueuedConnection)
    webUpdateStatus.adminModeStateRequested.connect(adminModeTracker.informAboutActualState, QtCore.Qt.QueuedConnection)
    webUpdateStatus.adminModeServerRequest.connect(adminModeTracker.triggerAdminModeChange, QtCore.Qt.QueuedConnection)

    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+a"), applicationWindow, adminModeTracker.triggerAdminModeChange)
    adminModeTracker.adminModeInfoState.connect(applicationWindow.onAdminMode)
    adminModeTracker.adminModeLeaveTime.connect(applicationWindow.onAdminRemaining)
    applicationWindow.adminModeLeaveButton.connect(adminModeTracker.disableAdminMode)


def main():
    os.environ["QML2_IMPORT_PATH"]="resources/kbstyle"
    os.environ["QT_IM_MODULE"]="qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_LAYOUT_PATH"]="resources/kbstyle/layouts"
    os.environ["QT_VIRTUALKEYBOARD_STYLE"]="blue_app_kb"
    #os.environ["QT_LOGGING_RULES"]="qt.virtualkeyboard=true"

    LoggingService.init()
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()
    AppSettings.restoreTimeZone()

    timerService = TimerService()
    updateStatusTimerService = TimerService()
    moneyTracker = MoneyTracker()

    gpioService = GpioService()
    adminModeTracker = AdminModeTracker(gpioService)

    webUpdateStatus = WebSocketStatus(sys.argv[1], moneyTracker)
    updateStatusTimerService.addTimerWorker(webUpdateStatus)

    application = ApplicationWindow.ApplicationWindow(timerService, moneyTracker)

    #app.setOverrideCursor(QtCore.Qt.BlankCursor)

    connectAdminModeTracker(adminModeTracker, application, webUpdateStatus)
    application.show()
    webUpdateStatus.asyncConnect()

    ret = app.exec_()
    gpioService.cleanup()
    application.cleanup()
    webUpdateStatus.asyncDisconnect()
    updateStatusTimerService.quit()
    timerService.quit()
    sys.exit(ret)

if __name__ == "__main__":
    main()
