from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.MainWindow import Ui_MainWindow

import SettingsWindow
import WifiSettingsWindow
from services.BluetoothService import BluetoothService
from services.CreditService import CreditService
from services.AppSettings import AppSettings
from services.TemperatureStatus import TemperatureStatus
from services.WirelessService import WirelessService


class ApplicationWindow(QtWidgets.QMainWindow):

    DISCONNECT_STR = 0
    SCAN_STR = 1
    CONNECTED_STR = 2
    CONNECTING_STR = 3
    CONNECTION_ERR_STR = 4
    CONNECTION_FAILED_STR = 5
    SCANNING_STR = 6
    NO_CREDIT_HEAD = 7
    NO_CREDIT = 8
    SECONDS = 9
    CPU_TEMP = 10

    def createTrTexts(self):
        return [ self.tr("Time to disconnect: {}s"), self.tr("Scan bluetooth network"), self.tr("Connected to the device: "),
        self.tr("Connecting to the device: "), self.tr("Connection error"), self.tr("Connection with {} failed"), self.tr("Scanninng..."),
        self.tr("No credit"), self.tr("Zero credit, insert money first please!"), self.tr("seconds"), self.tr("CPU temp: {}") ]

    def __init__(self, timerService):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showFullScreen()
        self.bluetoothService = BluetoothService(timerService)
        self.bluetoothService.disconnectedBeginSignal.connect(self.onDisconnected)
        self.bluetoothService.disconnectedEndSignal.connect(self.setWidgetsEnabled)
        self.bluetoothService.refreshTimerSignal.connect(lambda value: self.ui.remainingTimeLabel.setText(self.texts[self.DISCONNECT_STR].format(str(value))))
        self.bluetoothService.connectedSignal.connect(self.onConnectedSignal)
        self.bluetoothService.connectionStrengthSignal.connect(lambda x: self.ui.signalStrengthProgressBar.setValue(x))
        self.temperatureStatus = TemperatureStatus()
        self.temperatureStatus.actualTemperature.connect( lambda value: self.ui.labelCpuTemp.setText(self.texts[self.CPU_TEMP].format(str(value))))
        self.setDemoModeVisible(False)
        self.ui.adminSettingsButton.setVisible(False)
        self.ui.wifiSettingsButton.setVisible(False)
        self.ui.addCreditButton.clicked.connect(lambda: self.creditService.changeCredit(10))
        self.ui.adminSettingsButton.clicked.connect(self.onAdminSettingsButton)
        self.ui.wifiSettingsButton.clicked.connect(lambda: WifiSettingsWindow.WifiSettingsWindow(self.wirelessService).exec())
        self.ui.scanButton.clicked.connect(self.onScanButton)
        self.ui.connectButton.clicked.connect(self.onConnectButton)
        self.ui.disconnectButton.clicked.connect(self.bluetoothService.forceDisconnect)
        self.ui.devicesWidget.itemSelectionChanged.connect(self.onSelectionChanged)
        self.texts = self.createTrTexts()
        self.creditService = CreditService(AppSettings.actualCoinSettings())
        self.creditService.creditChanged.connect(self.onCreditChange, QtCore.Qt.QueuedConnection)
        self.creditService.changeCredit(0)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+a"), self, self.onAdminMode)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+d"), self, lambda: self.setDemoModeVisible(not self.ui.cpuTempValueLabel.isVisible()))
        timerService.addTimerWorker(self.temperatureStatus)

        self.wirelessService = WirelessService()
        self.wirelessService.stateChanged.connect(self.wirelessServiceStateChanged)
        self.wirelessService.start()
    
    def onAdminMode(self):
        self.ui.adminSettingsButton.setVisible(not self.ui.adminSettingsButton.isVisible())
        self.ui.wifiSettingsButton.setVisible(not self.ui.wifiSettingsButton.isVisible())

    def onAdminSettingsButton(self):
        SettingsWindow.SettingsWindow().exec()
        self.creditService.setCoinSettings(AppSettings.actualCoinSettings())

    def onDisconnected(self):
        self.ui.connectInfoLabel.clear()
        self.ui.connectDeviceLabel.clear()
        self.ui.remainingTimeLabel.clear()
        self.ui.devicesWidget.setRowCount(0)
        self.ui.disconnectButton.setEnabled(False)
        self.ui.signalStrengthProgressBar.setEnabled(False)
        self.ui.signalStrengthLabel.setEnabled(False)
        self.ui.signalStrengthProgressBar.setValue(0)
        self.creditService.clearCredit()

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
        data = self.bluetoothService.scan()
        self.ui.devicesWidget.setRowCount(len(data))
        for index, item in enumerate(data):
            self.ui.devicesWidget.setItem(index,0, QtWidgets.QTableWidgetItem(str(item[0])))
            self.ui.devicesWidget.setItem(index,1, QtWidgets.QTableWidgetItem(str(item[1])))

        self.setWidgetsEnabled()
        self.ui.scanButton.setText(self.texts[self.SCAN_STR])

    def onConnectButton(self):
        if self.creditService.getCredit() == 0.0:
            QtWidgets.QMessageBox.critical(self, self.texts[self.NO_CREDIT_HEAD], self.texts[self.NO_CREDIT], QtWidgets.QMessageBox.Cancel)
            return

        self.setWidgetsDisabled() 
        macAddr = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 1).text()[1:-1]
        deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
        self.ui.connectInfoLabel.setText(self.texts[self.CONNECTING_STR])
        self.ui.connectDeviceLabel.setText(deviceName + " (" + macAddr + ")")
        self.bluetoothService.connect(macAddr, self.creditService.getCredit())

    def onConnectedSignal(self, exitCode):
        if exitCode == 1:
            deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
            QtWidgets.QMessageBox.critical(self, self.texts[self.CONNECTION_ERR_STR], self.texts[self.CONNECTION_FAILED_STR].format(deviceName), QtWidgets.QMessageBox.Cancel)
            self.ui.connectInfoLabel.clear()
            self.ui.connectDeviceLabel.clear()
            self.setWidgetsEnabled()
            self.ui.connectButton.setEnabled(True)
        else:
            macAddr = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 1).text()[1:-1]
            deviceName = self.ui.devicesWidget.item(self.ui.devicesWidget.selectionModel().selectedRows()[0].row(), 0).text()
            self.ui.connectInfoLabel.setText(self.texts[self.CONNECTED_STR])
            self.ui.connectDeviceLabel.setText(deviceName + " (" + macAddr + ")")
            self.ui.disconnectButton.setEnabled(True)
            self.ui.signalStrengthProgressBar.setEnabled(True)
            self.ui.signalStrengthLabel.setEnabled(True)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            newTexts = self.createTrTexts()
            for i in [self.ui.connectInfoLabel, self.ui.scanButton, self.ui.remainingTimeLabel]:
                if i.text() != "":
                    i.setText(newTexts[self.texts.index(i.text())])
            self.texts = newTexts
            self.ui.retranslateUi(self)
        super(ApplicationWindow, self).changeEvent(event)

    def setDemoModeVisible(self, value):
        self.ui.cpuTempValueLabel.setVisible(value)
        self.ui.labelCpuTemp.setVisible(value)
        self.ui.addCreditButton.setVisible(value)
        self.ui.disconnectButton.setVisible(value)
        if value:
            self.temperatureStatus.start()
        else:
            self.temperatureStatus.stop()

    def cleanup(self):
        self.creditService.cleanup()

    def wirelessServiceStateChanged(self, state, ssid):
        text = state
        if ssid != "":
            text = text + " - " + ssid
        self.ui.wifiStateLabel.setText(text)

    def onCreditChange(self, credit):
        self.ui.actualCreditValue.setText(str(int(self.creditService.getCredit())) + " " + self.texts[self.SECONDS])
        if self.bluetoothService.isConnected() and (credit > 0):
            self.bluetoothService.updateDuration(credit)
        else:
            pass

