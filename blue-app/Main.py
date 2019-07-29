from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

import ApplicationWindow

from services.AppSettings import AppSettings
from services.TimerService import TimerService
from services.UpdateStatus import UpdateStatus

def main():
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()

    timerService = TimerService()
    updateStatus = UpdateStatus()
    timerService.addTimerWorker(updateStatus)

    application = ApplicationWindow.ApplicationWindow(timerService)
    #t.start()
    #app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    ret = app.exec_()
    application.cleanup()
    timerService.quit()
    sys.exit(ret)

if __name__ == "__main__":
    main()
