from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

import ApplicationWindow

from services.AppSettings import AppSettings
from services.TimerService import TimerService
from services.UpdateStatus import WebSocketStatus
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker

def main():
    LoggingService.init()
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()
    AppSettings.restoreTimeZone()

    timerService = TimerService()
    updateStatusTimerService = TimerService()
    moneyTracker = MoneyTracker()

    webUpdateStatus = WebSocketStatus(sys.argv[1], moneyTracker)
    updateStatusTimerService.addTimerWorker(webUpdateStatus)

    application = ApplicationWindow.ApplicationWindow(timerService, moneyTracker)

    #t.start()
    #app.setOverrideCursor(QtCore.Qt.BlankCursor)

    application.adminModeStateChanged.connect(webUpdateStatus.onAdminModeUIChange, QtCore.Qt.QueuedConnection)
    webUpdateStatus.adminModeUIStateRequested.connect(application.adminModeStateRequest, QtCore.Qt.QueuedConnection)
    application.show()

    webUpdateStatus.adminModeRequested.connect(application.onAdminMode, QtCore.Qt.QueuedConnection)
    webUpdateStatus.asyncConnect()

    ret = app.exec_()
    application.cleanup()
    webUpdateStatus.asyncDisconnect()
    updateStatusTimerService.quit()
    timerService.quit()
    sys.exit(ret)

if __name__ == "__main__":
    main()
