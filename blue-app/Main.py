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
        self.ui.connectButton.clicked.connect(self.onConnectButton)

    def setWidgetsEnabled(self):
        self.ui.scanButton.setEnabled(True)
        self.ui.connectButton.setEnabled(True)
        self.ui.devicesWidget.setEnabled(True)

    def setWidgetsDisabled(self):
        self.ui.scanButton.setEnabled(False)
        self.ui.connectButton.setEnabled(False)
        self.ui.devicesWidget.setEnabled(False)

    def onScanButton(self):
        self.setWidgetsDisabled()
        QtCore.QCoreApplication.processEvents()
        returnCode = QtCore.QProcess.execute("scripts/bt-scan-sh")
        processGetDevices = QtCore.QProcess()
        processGetDevices.start("scripts/bt-list-device.sh")
        if (processGetDevices.waitForFinished()):
            self.ui.devicesWidget.clear()
            data = processGetDevices.readAllStandardOutput().data().decode('utf-8').splitlines()
            self.ui.devicesWidget.setRowCount(len(data))
            for index, itemStr in enumerate(data):
                self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(itemStr))

        self.setWidgetsEnabled()

    def onConnectButton(self):
        self.setWidgetsDisabled() 

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    app.setOverrideCursor(QtCore.Qt.BlankCursor)
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
