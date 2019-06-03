from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.MainWindow import Ui_MainWindow
import sys

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.scanButton.clicked.connect(self.onScanButton)

    def setWidgetsStatus(self, value):
        self.ui.scanButton.setEnabled(value)
        self.ui.connectButton.setEnabled(value)
        self.ui.devicesWidget.setEnabled(value)

    def onScanButton(self):
        self.setWidgetsStatus(False)

    def onConnectButton(self):
        self.setWidgetsStatus(False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
