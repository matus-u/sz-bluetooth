from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys

import ApplicationWindow
from services.AppSettings import AppSettings

def main():
    app = QtWidgets.QApplication(sys.argv)
    AppSettings.restoreLanguage()

    application = ApplicationWindow.ApplicationWindow()
    #app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
