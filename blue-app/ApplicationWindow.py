from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.MainWindow import Ui_MainWindow

import SettingsWindow

class ApplicationWindow(QtWidgets.QMainWindow):

    DISCONNECT_STR = 0
    SCAN_STR = 1
    CONNECTED_STR = 2
    CONNECTING_STR = 3
    CONNECTION_ERR_STR = 4
    CONNECTION_FAILED_STR = 5
    SCANNING_STR = 6

    def createTrTexts(self):
        return [ self.tr("Time to disconnect: {}s"), self.tr("Scan bluetooth network"), self.tr("Connected to the device: "),
        self.tr("Connecting to the device: "), self.tr("Connection error"), self.tr("Connection with {} failed"), self.tr("Scanninng...") ]

    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()
        self.ui.adminSettingsButton.clicked.connect(self.onSettingsButton)
        self.ui.scanButton.clicked.connect(self.onScanButton)
        self.ui.connectButton.clicked.connect(self.onConnectButton)
        self.ui.devicesWidget.itemSelectionChanged.connect(self.onSelectionChanged)
        self.connectionTimer = QtCore.QTimer()
        self.connectionTimer.setSingleShot(True)
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.onRefreshTimer)
        self.connectionTimer.timeout.connect(self.onConnectionTimer)
        self.texts = self.createTrTexts()

    def onRefreshTimer(self):
        self.ui.remainingTimeLabel.setText(self.texts[self.DISCONNECT_STR].format(str(int(self.connectionTimer.remainingTime()/1000))))

    def onConnectionTimer(self):
        self.refreshTimer.stop()
        self.ui.connectInfoLabel.clear()
        self.ui.connectDeviceLabel.clear()
        self.ui.remainingTimeLabel.clear()
        self.ui.devicesWidget.setRowCount(0)
        QtCore.QCoreApplication.processEvents()
        QtCore.QProcess.execute("scripts/bt-cleanup-device.sh", [self.connectedDevice, self.connectedPid ])
        self.setWidgetsEnabled()

    def onSelectionChanged(self):
        if not self.ui.devicesWidget.selectedItems():
            self.ui.connectButton.setEnabled(False)
        else:
            self.ui.connectButton.setEnabled(True)

    def setWidgetsEnabled(self):
        self.ui.scanButton.setEnabled(True)
        self.ui.devicesWidget.setEnabled(True)

    def setWidgetsDisabled(self):
        self.ui.scanButton.setEnabled(False)
        self.ui.connectButton.setEnabled(False)
        self.ui.devicesWidget.setEnabled(False)

    def onScanButton(self):
        self.ui.devicesWidget.clear()
        self.setWidgetsDisabled()
        self.ui.scanButton.setText(self.texts[self.SCANNING_STR])
        QtCore.QCoreApplication.processEvents()
        returnCode = QtCore.QProcess.execute("scripts/bt-scan-sh")
        processGetDevices = QtCore.QProcess()
        processGetDevices.start("scripts/bt-list-device.sh")
        if (processGetDevices.waitForFinished()):
            data = processGetDevices.readAllStandardOutput().data().decode('utf-8').splitlines()
            self.ui.devicesWidget.setRowCount(len(data))
            for index, itemStr in enumerate(data):
                self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(" ".join(itemStr.split()[:-1])))
                self.ui.devicesWidget.setItem(index,1, QtWidgets.QTableWidgetItem(itemStr.split()[-1]))

        self.setWidgetsEnabled()
        self.ui.scanButton.setText(self.texts[self.SCAN_STR])

    def onConnectButton(self):
        self.setWidgetsDisabled() 
        macAddr = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 1).text()[1:-1]
        deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
        self.process = QtCore.QProcess()
        self.process.finished.connect(self.onConnect)
        self.ui.connectInfoLabel.setText(self.texts[self.CONNECTING_STR])
        self.ui.connectDeviceLabel.setText(deviceName + " (" + macAddr + ")")
        self.process.start("scripts/bt-connect-with-timeout.sh", [ macAddr, "15" ])

    def onConnect(self, exitCode, exitStatus):
        macAddr = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 1).text()[1:-1]
        deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()

        if exitCode == 1:
            QtWidgets.QMessageBox.critical(self, self.texts[self.CONNECTION_ERR_STR], self.texts[self.CONNECTION_FAILED_STR].format(deviceName), QtWidgets.QMessageBox.Cancel)
            self.ui.connectInfoLabel.clear()
            self.ui.connectDeviceLabel.clear()
            self.setWidgetsEnabled()
            self.ui.connectButton.setEnabled(True)
        else:
            self.connectedPid = self.process.readAllStandardOutput().data().decode('utf-8').splitlines()[-1]
            self.connectedDevice = macAddr
            self.ui.connectInfoLabel.setText(self.texts[self.CONNECTED_STR])
            self.ui.connectDeviceLabel.setText(deviceName + " (" + macAddr + ")")
            self.connectionTimer.start(30000)
            self.onRefreshTimer()
            self.refreshTimer.start(1000)

    def onSettingsButton(self):
        SettingsWindow.SettingsWindow().exec()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            newTexts = self.createTrTexts()
            for i in [self.ui.connectInfoLabel, self.ui.scanButton, self.ui.remainingTimeLabel]:
                if i.text() != "":
                    i.setText(newTexts[self.texts.index(i.text())])
            self.texts = newTexts
            self.ui.retranslateUi(self)
        super(ApplicationWindow, self).changeEvent(event)
