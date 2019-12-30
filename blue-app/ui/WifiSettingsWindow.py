from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WifiSettings import Ui_WifiSettings

from services.AppSettings import AppSettings
from services.WirelessService import WirelessService, WirelessScan

class WifiSettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, wirelessService):
        super(WifiSettingsWindow, self).__init__(parent)
        self.ui = Ui_WifiSettings()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.scanWifiButton.clicked.connect(self.onScanButton)
        self.ui.apListWidget.itemSelectionChanged.connect(self.onSelectionChanged)

        self.ui.wifiEnabledCheckBox.toggled.connect(self.wifiCheckBoxChanged)
        self.ui.wifiEnabledCheckBox.setChecked(AppSettings.actualWirelessEnabled())
        self.ui.ssidLineEdit.setText(AppSettings.actualWirelessSSID())
        self.ui.wifiPassLineEdit.setText(AppSettings.actualWirelessPassword())

        self.wirelessService = wirelessService

    def onOkButton(self):
        AppSettings.storeWirelessSettings(self.ui.wifiEnabledCheckBox.isChecked(), self.ui.ssidLineEdit.text(), self.ui.wifiPassLineEdit.text())
        if (self.ui.wifiEnabledCheckBox.isChecked()):
            self.wirelessService.connect()
        else:
            self.wirelessService.stop()
        self.accept()

    def onScanButton(self):
        data = WirelessScan().scan()
        self.ui.apListWidget.clear()
        self.ui.apListWidget.setRowCount(len(data))
        for index, itemStr in enumerate(data):
            self.ui.apListWidget.setItem(index,0, QtWidgets.QTableWidgetItem(itemStr))

    def onSelectionChanged(self):
        text = self.ui.apListWidget.item(self.ui.apListWidget.selectionModel().selectedRows()[0].row(), 0).text()
        if text is not "":
            self.ui.ssidLineEdit.setText(text)

    def wifiCheckBoxChanged(self, state):
        self.ui.ssidLineEdit.setEnabled(state)
        self.ui.wifiPassLineEdit.setEnabled(state)
        self.ui.scanWifiButton.setEnabled(state)

