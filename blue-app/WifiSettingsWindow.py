from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WifiSettings import Ui_WifiSettings

from services.AppSettings import AppSettings
from services.WirelessService import WirelessService, WirelessScan

class WifiSettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(WifiSettingsWindow, self).__init__()
        self.ui = Ui_WifiSettings()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.ssidLineEdit.setText(AppSettings.actualWirelessSSID())
        self.ui.wifiPassLineEdit.setText(AppSettings.actualWirelessPassword())
        self.ui.scanWifiButton.clicked.connect(self.onScanButton)
        self.ui.apListWidget.itemSelectionChanged.connect(self.onSelectionChanged)


    def onOkButton(self):
        AppSettings.storeWirelessSettings(self.ui.ssidLineEdit.text(), self.ui.wifiPassLineEdit.text())
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

