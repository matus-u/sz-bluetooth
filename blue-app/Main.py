from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

import ApplicationWindow
import UpdateStatusThread
from services.AppSettings import AppSettings

def main():
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()

    application = ApplicationWindow.ApplicationWindow()
    t = UpdateStatusThread.UpdateStatusThread()
    t.start()
    #app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    ret = app.exec_()
    application.cleanup()
    sys.exit(ret)

if __name__ == "__main__":
    main()
