from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

import ApplicationWindow

from services.AppSettings import AppSettings
from services.TimerService import TimerService
from services.UpdateStatus import UpdateStatus
from services.LoggingService import LoggingService
from services.MoneyTracker import MoneyTracker

def main():
    LoggingService.init()
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()
    AppSettings.restoreTimeZone()

    timerService = TimerService()
    moneyTracker = MoneyTracker()
    updateStatus = UpdateStatus(sys.argv[1], moneyTracker)
    timerService.addTimerWorker(updateStatus)

    application = ApplicationWindow.ApplicationWindow(timerService, moneyTracker)
    #t.start()
    #app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    ret = app.exec_()
    application.cleanup()
    timerService.quit()
    sys.exit(ret)

if __name__ == "__main__":
    main()
